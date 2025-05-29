import os
import boto3
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_s3_client():
    """Create and return an S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

def upload_file_to_s3(file_path, bucket, s3_key):
    """Upload a single file to S3."""
    try:
        s3_client = get_s3_client()
        s3_client.upload_file(file_path, bucket, s3_key)
        logger.info(f"Successfully uploaded {file_path} to s3://{bucket}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error uploading {file_path}: {str(e)}")
        return False

def upload_climate_data():
    """Upload all climate data files to S3 raw zone."""
    raw_bucket = os.getenv('S3_RAW_BUCKET')
    data_dir = 'data'  # Directory containing climate data files
    
    if not os.path.exists(data_dir):
        logger.error(f"Data directory {data_dir} does not exist")
        return
    
    # Get current timestamp for versioning
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            local_path = os.path.join(data_dir, filename)
            s3_key = f"raw/{timestamp}/{filename}"
            
            if upload_file_to_s3(local_path, raw_bucket, s3_key):
                logger.info(f"Successfully processed {filename}")
            else:
                logger.error(f"Failed to process {filename}")

if __name__ == "__main__":
    upload_climate_data() 