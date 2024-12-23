import boto3
import pandas as pd
import pdfplumber
from io import BytesIO
from datetime import datetime
import logging
import os
import time

# Initialize S3 client
s3_client = boto3.client('s3')

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log file with timestamp
    log_filename = f"logs/processing_time_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Keep console output too
        ]
    )
    return logging.getLogger(__name__)

def list_files_in_directory(bucket_name, directory, logger):
    """
    Lists all files in a specified directory of an S3 bucket.
    
    :param bucket_name: Name of the S3 bucket
    :param directory: Directory path in the S3 bucket
    :return: List of file keys
    """
    
    try:
        # First verify the bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        
        # List objects with detailed logging
        logger.info(f"Attempting to list files in bucket: {bucket_name}, directory: {directory}")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory)
        
        if response.get('KeyCount', 0) == 0:
            logger.warning(f"No files found in {bucket_name}/{directory}")
            # List root directory contents to help debug
            root_response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="")
            logger.info(f"Root directory contents: {[content['Key'] for content in root_response.get('Contents', [])]}")
            
        return [content['Key'] for content in response.get('Contents', []) if not content['Key'].endswith('/')]
        
    except s3_client.exceptions.NoSuchBucket:
        logger.error(f"Bucket {bucket_name} does not exist")
        raise Exception(f"Bucket {bucket_name} does not exist")
    except s3_client.exceptions.ClientError as e:
        logger.error(f"Error accessing S3: {str(e)}")
        raise Exception(f"Error accessing S3: {str(e)}")


def read_pdf_from_s3(bucket_name, key):
    """
    Reads a PDF file from S3 and extracts its content.
    
    :param bucket_name: Name of the S3 bucket
    :param key: Object key in S3
    :return: List of extracted data
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    pdf_content = response['Body'].read()
    
    extracted_data = []
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            # Extract text or tables as needed
            extracted_data.append(page.extract_text())
    return extracted_data


def write_parquet_to_s3(df, bucket_name, key):
    """
    Writes a Pandas DataFrame to S3 in Parquet format.
    
    :param df: Pandas DataFrame to write
    :param bucket_name: Name of the S3 bucket
    :param key: Object key in S3 where the Parquet file will be stored
    """
    buffer = BytesIO()
    df.to_parquet(buffer, engine='pyarrow', index=False)
    buffer.seek(0)
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=buffer.getvalue())


def process_multiple_directories(bucket_name, directories, logger):
    """
    Processes multiple directories in the S3 bucket.
    
    :param bucket_name: S3 bucket name
    :param directories: List of tuples containing input and output directory pairs
    """
    for input_directory, output_directory in directories:
        logger.info(f"Processing directory: {input_directory} -> {output_directory}")
        logger.info("Started time: %s", datetime.now())
        process_directory(bucket_name, input_directory, output_directory, logger)
        logger.info("Finished time: %s", datetime.now())


def extract_paper_metadata(text):
    """
    Attempt to extract common academic paper metadata.
    """
    # Simple heuristic extraction - could be improved with regex or NLP
    metadata = {
        'title': '',
        'abstract': '',
        'authors': [],
        'year': None,
        'references': [],
    }
    
    # Find common paper sections
    lines = text.split('\n')
    current_section = ''
    
    for line in lines[:100]:  # Look in first 100 lines for metadata
        line = line.strip()
        lower_line = line.lower()
        
        if 'abstract' in lower_line:
            current_section = 'abstract'
        elif 'introduction' in lower_line:
            break
        elif current_section == 'abstract' and line:
            metadata['abstract'] += line + ' '
        elif not metadata['title'] and len(line) > 20:  # Usually first long line is title
            metadata['title'] = line
            
    return metadata

def process_pdf_data_to_dataframe(data, pdf_key, extract_metadata=True):
    """
    Enhanced PDF processing with metadata extraction and text sections.
    """
    filename = pdf_key.split('/')[-1]
    full_text = ' '.join(data)
    
    # # Basic paper data
    # paper_dict = {
    #     'filename': filename,
    #     'full_text': full_text,
    #     'source_path': pdf_key,
    #     'num_pages': len(data),
    #     'processed_date': pd.Timestamp.now(),
    # }

    paper_dict = {
        'filename': filename,
        'full_text': full_text,
    }
    
    # Extract and add metadata if requested
    if extract_metadata:
        metadata = extract_paper_metadata(full_text)
        paper_dict.update(metadata)
    
    return pd.DataFrame([paper_dict])

def write_parquet_with_compression(df, bucket_name, key):
    """
    Write Parquet with optimized compression settings.
    """
    buffer = BytesIO()
    
    # Configure compression and encoding for different columns
    compression = {
        'filename': 'snappy',
        'full_text': 'gzip',  # Better compression for text
    }
    
    df.to_parquet(
        buffer,
        engine='pyarrow',
        index=False,
        compression=compression,
        coerce_timestamps='ms'
    )
    
    buffer.seek(0)
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=buffer.getvalue())


def process_directory(bucket_name, input_directory, output_directory, logger):
    """
    Process PDFs with batching and error handling.
    """
    start_time = time.time()
    pdf_files = list_files_in_directory(bucket_name, input_directory)
    all_papers = pd.DataFrame()
    batch_size = 50
    failed_files = []
    
    for i in range(0, len(pdf_files), batch_size):
        batch_papers = pd.DataFrame()
        batch = pdf_files[i:i + batch_size]
        
        logger.info("Start reading pdf from s3.")
        for pdf_key in batch:
            try:
                logger.info(f"Processing file: {pdf_key}")
                pdf_data = read_pdf_from_s3(bucket_name, pdf_key)
                paper_df = process_pdf_data_to_dataframe(pdf_data, pdf_key)
                batch_papers = pd.concat([batch_papers, paper_df], ignore_index=True)
            except Exception as e:
                logger.error(f"Error processing {pdf_key}: {str(e)}")
                failed_files.append((pdf_key, str(e)))
        
        logger.info("Batch size: %d", len(batch))
        logger.info("Read pdf from s3, convert to dataframe, and concat.")
        # Save batch
        logger.info("Start writing batch to s3.")
        batch_output_key = f"{output_directory}/papers_batch_{i//batch_size}.parquet"
        write_parquet_with_compression(batch_papers, bucket_name, batch_output_key)
        logger.info(f"Saved batch: {batch_output_key}")
        
        # Optional: Save failed files list
        if failed_files:
            failed_df = pd.DataFrame(failed_files, columns=['filename', 'error'])
            error_key = f"{output_directory}/failed_files.parquet"
            write_parquet_with_compression(failed_df, bucket_name, error_key)

    logger.info("Processed %d files in %s", len(pdf_files), input_directory)

# Example usage
if __name__ == "__main__":
    bucket_name = "chjun-bucket1"
    directories = [
        ("papers/", "papers_parquet/"), 
        ("electron_papers/", "electron_parquets/"), 
    ]
    logger = setup_logging()
    logger.info("Start processing multiple directories.")
    process_multiple_directories(bucket_name, directories, logger)
    logger.info("Processing completed for all directories.")
