import boto3
from PIL import Image
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

BUCKET_NAME = 'monlam.ai.ocr'
DIRECTORY_PREFIX = 'Style_classification/works/manuscript_works/'
OUTPUT_FORMAT = 'JPEG'
EXCLUDE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
JPEG_EXTENSION = '.jpg'
MAX_WORKERS = 10  # Number of concurrent workers

s3_client = boto3.client('s3')

def list_directories(bucket, prefix):
    """List directories within a given prefix in an S3 bucket."""
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/')

    directories = []
    for page in page_iterator:
        if 'CommonPrefixes' in page:
            for common_prefix in page['CommonPrefixes']:
                directories.append(common_prefix['Prefix'])
    return directories

def list_images(bucket, directories):
    """List image files within given directories in an S3 bucket."""
    image_keys = []
    for directory in directories:
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=directory)

        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    ext = os.path.splitext(key)[1].lower()
                    if ext not in EXCLUDE_EXTENSIONS:
                        image_keys.append(key)
    return image_keys

def convert_image_to_jpeg(image_bytes):
    with Image.open(io.BytesIO(image_bytes)) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        output_buffer = io.BytesIO()
        img.save(output_buffer, format=OUTPUT_FORMAT, quality=95)
        return output_buffer.getvalue()

def process_image(bucket, key):
    """Process a single image file."""
    print(f"Processing {key}...")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_bytes = response['Body'].read()

        jpeg_bytes = convert_image_to_jpeg(image_bytes)

        base_key = os.path.splitext(key)[0]
        jpeg_key = base_key + JPEG_EXTENSION

        s3_client.put_object(Bucket=bucket, Key=jpeg_key, Body=jpeg_bytes, ContentType='image/jpeg')
        print(f"Uploaded {jpeg_key}")

        s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"Deleted original {key}")

    except Exception as e:
        print(f"Error processing {key}: {e}")

def main():
    print("Listing directories...")
    directories = list_directories(BUCKET_NAME, DIRECTORY_PREFIX)
    print(f"Found {len(directories)} directories to process.")

    if not directories:
        print("No directories to process.")
        return

    print("Listing images...")
    image_keys = list_images(BUCKET_NAME, directories)
    print(f"Found {len(image_keys)} images to convert.")

    if not image_keys:
        print("No images to convert.")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_image, BUCKET_NAME, key) for key in image_keys]
        for future in as_completed(futures):
            future.result()

    print("Conversion completed.")

if __name__ == "__main__":
    main()
