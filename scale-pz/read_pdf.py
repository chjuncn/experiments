    # read pdf from s3 and write to disk as text
import boto3
import PyPDF2
import os
from io import BytesIO
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_and_convert_pdfs(bucket_name, directory1, directory2, local_output_dir):
    """
    Download PDFs from two S3 directories and convert them to text files
    
    Args:
        bucket_name (str): Name of the S3 bucket
        directory1 (str): First S3 directory path
        directory2 (str): Second S3 directory path
        local_output_dir (str): Local directory to save text files
    """
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Create output directory if it doesn't exist
    os.makedirs(local_output_dir, exist_ok=True)
    
    # Process both directories
    for directory in [directory1, directory2]:
        # List objects in the directory
        list_start_time = time.time()
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=directory
        )
        list_time = time.time() - list_start_time
        logger.info(f"Time taken for listing: {list_time:.2f} seconds")
        
        # Process each PDF file
        for obj in response.get('Contents', []):
            start_time = time.time()
            if obj['Key'].lower().endswith('.pdf'):
                # Download PDF file
                response = s3_client.get_object(
                    Bucket=bucket_name,
                    Key=obj['Key']
                )
                
                pdf_file = BytesIO(response['Body'].read())
                
                try:
                    # Read PDF
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Extract text from all pages
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    
                    # Create output filename
                    output_filename = os.path.splitext(os.path.basename(obj['Key']))[0] + '.txt'
                    output_path = os.path.join(local_output_dir, output_filename)
                    
                    # Write text to file
                    # with open(output_path, 'w', encoding='utf-8') as f:
                    #     f.write(text)
                    logger.info(f"Time taken for {obj['Key']}: {time.time() - start_time:.2f} seconds")
                    logger.info(f"Successfully converted {obj['Key']} to {output_path}")
                    
                except Exception as e:
                    logger.error(f"Error processing {obj['Key']}: {str(e)}")

if __name__ == "__main__":
    # Example usage
    BUCKET_NAME = "chjun-bucket1"
    DIRECTORY1 = "electron_papers/"
    DIRECTORY2 = "papers/"
    OUTPUT_DIR = "output_texts"
    
    download_and_convert_pdfs(BUCKET_NAME, DIRECTORY1, DIRECTORY2, OUTPUT_DIR)