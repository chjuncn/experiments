import duckdb
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import os
import s3fs
import logging
import time
from datetime import datetime
import concurrent.futures
from functools import partial
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import gc
import psutil
import glob
import os   
import threading

bucket_name = "chjun-bucket1"
s3_papers_path = f"s3://{bucket_name}/papers_parquets/*.parquet"
s3_electron_path = f"s3://{bucket_name}/electron_parquets/*.parquet"

PARQUET_QUERY_TEMPLATE = """
SELECT 
    filename,
    LEFT(full_text, 100) as first_100_chars
FROM arrow_table
"""

PARQUET_QUERY_TEMPLATE_FULLTEXT = """
SELECT 
    filename,
    full_text
FROM arrow_table
"""

PARQUET_QUERY_TEMPLATE_FILENAMES = """
SELECT
   filename
FROM arrow_table
"""

# Set up logger
def setup_logger():
    #delete old log files
    for file in glob.glob('logs/duckdb_arrow_parquet_s3_processing_log_*.log'):
        os.remove(file)

    """Configure logger with timestamp and format"""
    logger = logging.getLogger('parquet_processor')
    logger.setLevel(logging.INFO)
    
    # Create handlers
    c_handler = logging.StreamHandler()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    f_handler = logging.FileHandler(f'logs/duckdb_arrow_parquet_s3_processing_log_{timestamp}.log')
    
    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    c_format = logging.Formatter(log_format)
    f_format = logging.Formatter(log_format)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    
    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    return logger


def load_parquet_file(file_path, logger):
    """Helper function to load a single parquet file"""
    try:
        table = pq.read_table(
            file_path,
            columns=['filename','full_text'],
            use_threads=True  # Can use internal threading safely
        )
        return table
    except Exception as e:
        return None


def log_memory_usage(logger):
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")


def process_files_in_chunks(file_patterns, query_template, chunk_size=5, max_workers=4, output_path="output.csv", logger=None):
    """
    Processes Parquet files in chunks using Apache Arrow and DuckDB.
    """
    logger.info("EXPERIMENT_CONFIG: {{" + 
                f"'max_workers': {max_workers}, " +
                f"'chunk_size': {chunk_size}, " +
                "'duckdb_threads': duckdb.sql('SELECT current_setting(''threads'')').fetchone()[0]" +
                "}}")
    
    combined_results = None
    s3 = s3fs.S3FileSystem()
    
    # Get all matching files from all patterns
    start_time = time.time()
    all_files = []
    for pattern in file_patterns:
        logger.info(f"Listing files for pattern: {pattern}")
        matching_files = s3.glob(pattern.replace('s3://', ''))
        all_files.extend([f's3://{f}' for f in matching_files])
    logger.info(f"File listing completed. Total files found: {len(all_files)}")
    logger.info(f"Time taken for file listing: {time.time() - start_time:.2f} seconds")

    # Process files in chunks
    total_processing_time = 0
    performance_stats = {
        'chunks_processed': 0,
        'files_processed': 0,
        'total_load_time': 0,
        'total_query_time': 0,
        'failures': 0
    }
    con = duckdb.connect()
    # pa.set_cpu_count(12)
    # pa.set_io_thread_count(12)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, len(all_files), chunk_size):
            chunk = all_files[i:i + chunk_size]
            chunk_start_time = time.time()
            logger.info(f"Processing chunk {i//chunk_size + 1}/{(len(all_files)-1)//chunk_size + 1} "
                       f"(files {i + 1} to {i + len(chunk)})")

            try:
                # Step 1: Load chunk into Arrow Table
                load_start_time = time.time()
                # Parallel file loading
                futures = []
                for file in chunk:
                    futures.append((executor.submit(load_parquet_file, file, logger), file))
                
                tables = []
                for future, file in futures:
                    try:
                        table = future.result()
                        if table is not None:
                            tables.append(table)
                    except Exception as e:
                        logger.error(f"Error in parallel loading: {str(e)}")
                        performance_stats['failures'] += 1
                
                if tables:
                    arrow_table = pa.concat_tables(tables)
                    load_time = time.time() - load_start_time
                    logger.info(f"Time taken for loading chunk: {load_time:.2f} seconds")
                    performance_stats['total_load_time'] += load_time

                    # Step 2: Query with DuckDB
                    query_start_time = time.time()
                    
                    con.register('arrow_table', arrow_table)
                    
                    result = [con.execute(q).df() for q in query_template]
                    query_time = time.time() - query_start_time
                    logger.info(f"Time taken for querying chunk: {query_time:.2f} seconds")
                    performance_stats['total_query_time'] += query_time
                    performance_stats['chunks_processed'] += 1
                    performance_stats['files_processed'] += len(chunk)

                    # Step 3: Append Results
                    if combined_results is None:
                        combined_results = result
                    else:
                        combined_results = pd.concat([combined_results, result], ignore_index=True)

                    # Cleanup
                    con.unregister('arrow_table')
                    del tables
                    del arrow_table
                    del result

            except Exception as e:
                logger.error(f"Error processing chunk: {str(e)}")
                performance_stats['failures'] += 1
                continue

            chunk_time = time.time() - chunk_start_time
            total_processing_time += chunk_time
            logger.info(f"Total time for this chunk: {chunk_time:.2f} seconds")
            logger.info("----------------------------------------")

            log_memory_usage(logger)  # Add before and after processing each chunk

    con.close()
    # Save results
    if combined_results is not None:
        # combined_results.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")

    logger.info(f"Total processing time: {time.time() - start_time:.2f} seconds")
    
    logger.info("PERFORMANCE_METRICS: {" +
                f"'total_time': {time.time() - start_time:.2f}, " +
                f"'chunks_processed': {performance_stats['chunks_processed']}, " +
                f"'files_processed': {performance_stats['files_processed']}, " +
                f"'avg_load_time': {performance_stats['total_load_time']/performance_stats['chunks_processed']:.2f}, " +
                f"'avg_query_time': {performance_stats['total_query_time']/performance_stats['chunks_processed']:.2f}, " +
                f"'failures': {performance_stats['failures']}" +
                "}")

if __name__ == "__main__":
    logger = setup_logger()
    # Configure processing
    # Add experiment description
    logger.info("EXPERIMENT_SERIES: Testing different CPU counts and worker configurations")
    
    experiments = [
        {'cpu_count': 6, 'max_workers': 12, 'query_template': [PARQUET_QUERY_TEMPLATE_FULLTEXT], 'chunk_size': 100},
        {'cpu_count': 10, 'max_workers': 12, 'query_template': [PARQUET_QUERY_TEMPLATE_FULLTEXT], 'chunk_size': 100},
        {'cpu_count': 10, 'max_workers': 20, 'query_template': [PARQUET_QUERY_TEMPLATE_FULLTEXT], 'chunk_size': 100},
    ]
    output_path = f"duckdb_arrow_parquet_fulltext_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    for exp in experiments:
        logger.info(f"\nSTART_EXPERIMENT: Running with {exp['cpu_count']} CPU threads and {exp['max_workers']} workers")
        
        # Update DuckDB configuration
        duckdb.sql(f"SET threads={exp['cpu_count']}")

        # Process files
        process_files_in_chunks(
            [s3_papers_path, s3_electron_path],
            exp['query_template'],
            chunk_size=exp['chunk_size'],
            max_workers=exp['max_workers'],
            logger=logger,
            output_path=output_path
        )
        
        logger.info("END_EXPERIMENT")