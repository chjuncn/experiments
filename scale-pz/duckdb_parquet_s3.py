import duckdb
import logging
import time
from datetime import datetime
import multiprocessing
import psutil
import s3fs
import pandas as pd
import boto3
import glob
import os

def setup_duckdb_connection(s3):
    con = duckdb.connect()
    con.install_extension("httpfs")
    con.load_extension("httpfs")
    
    # Get credentials from boto3 session
    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name or 'us-east-1'
    
    # Set S3 credentials in DuckDB
    if credentials:
        con.execute(f"SET s3_region='{region}'")
        con.execute(f"SET s3_access_key_id='{credentials.access_key}'")
        con.execute(f"SET s3_secret_access_key='{credentials.secret_key}'")
        if credentials.token:  # For temporary credentials
            con.execute(f"SET s3_session_token='{credentials.token}'")

    return con


def setup_logger(name='parquet_processor'):
    """Configure logger with timestamp and format"""

    #delet old log files
    for file in glob.glob('logs/duckdb_parquet_s3_processing_log_*.log'):
        os.remove(file)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    c_handler = logging.StreamHandler()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    f_handler = logging.FileHandler(f'logs/duckdb_parquet_s3_processing_log_{timestamp}.log')
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    c_format = logging.Formatter(log_format)
    f_format = logging.Formatter(log_format)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    return logger

def log_memory_usage(logger):
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")


# Define the query template at module level
PARQUET_QUERY_TEMPLATE = """
SELECT 
    filename,
    LEFT(full_text, 100) as first_100_chars
FROM read_parquet([{file_list}])
"""

PARQUET_QUERY_TEMPLATE_FILENAMES = """
SELECT
   filename
FROM read_parquet([{file_list}])
"""

PARQUET_QUERY_TEMPLATE_FULLTEXT = """
SELECT
   filename,
   full_text
FROM read_parquet([{file_list}])
"""


def process_parquet_files(file_patterns, query_template, output_path="output.csv", logger=None):
    """
    Process Parquet files directly using DuckDB with chunking.
    
    Args:
        file_patterns (list): List of S3 path patterns to process.
        output_path (str): Path to save the results.
    """
    start_time = time.time()
    # Create S3 filesystem with explicit credentials
    s3 = s3fs.S3FileSystem(
        anon=False,  # Use AWS credentials
        use_ssl=True
    )
    
    try:
        # Get all matching files
        logger.info("Listing all files...")
        all_files = []
        for pattern in file_patterns:
            logger.info(f"Listing files for pattern: {pattern}")
            matching_files = s3.glob(pattern.replace('s3://', ''))
            all_files.extend([f's3://{f}' for f in matching_files])
        
        total_files = len(all_files)
        logger.info(f"File listing completed. Total files found: {total_files}")
        logger.info(f"Time taken for file listing: {time.time() - start_time:.2f} seconds")
        
        # Create connection for each chunk
        con = setup_duckdb_connection(s3)
        try:
            query_start = time.time()
            # Create the query for this chunk
            files_str = "', '".join(all_files)
            query = query_template.format(
                file_list=f"'{files_str}'"
            )

            # Execute query
            result = con.execute(query).df()
            process_time = time.time() - query_start
            logger.info(f"Total time for the files (loading + execution): {process_time:.2f} seconds")
            log_memory_usage(logger)
            logger.info("----------------------------------------")
            
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            raise Exception(f"Error processing files: {str(e)}")
        finally:
            con.close()
    
        # Save final results
        # result.to_csv(output_path, index=False)

        # Log final statistics
        total_time = time.time() - start_time
        logger.info("Processing Summary:")
        logger.info(f"Total files processed: {total_files}")
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    # Configure number of threads based on CPU cores
    logger = setup_logger()
    cpu_count = 6
    print(f"Using {cpu_count} threads for DuckDB processing")
    
    # Configure DuckDB
    duckdb.sql(f"SET threads={cpu_count}")
    
    # Define S3 paths
    bucket_name = "chjun-bucket1"
    s3_papers_path = f"s3://{bucket_name}/papers_parquets/*.parquet"
    s3_electron_path = f"s3://{bucket_name}/electron_parquets/*.parquet"
    
    # Process files
    file_paths = [s3_papers_path, s3_electron_path]
    process_parquet_files(
        file_paths,
        PARQUET_QUERY_TEMPLATE_FULLTEXT,
        logger=logger,
        output_path="duckdb_parquet_s3_output.csv"
    )