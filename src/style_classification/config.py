import os
import csv
import boto3

def get_aws_credentials():
    aws_credentials_file = os.path.join(os.getenv('USERPROFILE'), '.aws', 'credential', 'tenkal_accessKeys.csv')
    aws_access_key_id = ''
    aws_secret_access_key = ''

    with open(aws_credentials_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            aws_access_key_id, aws_secret_access_key = row
            break

    return aws_access_key_id, aws_secret_access_key


def get_s3_client(region_name='us-east-1'):
    aws_access_key_id, aws_secret_access_key = get_aws_credentials()
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
