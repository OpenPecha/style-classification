import os
import csv
import boto3

def get_aws_credentials():
    # Path to your custom CSV file
    aws_credentials_file = os.path.join(os.getenv('HOME'), '.aws_tk', 'credential', 'tenkal_accessKeys.csv')
    aws_access_key_id = ''
    aws_secret_access_key = ''

    # Check if the credentials file exists
    if not os.path.isfile(aws_credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {aws_credentials_file}")

    # Read credentials from the CSV file
    with open(aws_credentials_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) >= 2:
                aws_access_key_id = row[0].strip()
                aws_secret_access_key = row[1].strip()
                break

    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS credentials not found in the file.")

    return aws_access_key_id, aws_secret_access_key

def get_s3_client(region_name='us-east-1'):
    aws_access_key_id, aws_secret_access_key = get_aws_credentials()
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
