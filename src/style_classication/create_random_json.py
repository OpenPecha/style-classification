import os
import csv
import boto3
import random
import json

aws_credentials_file = os.path.join(
    os.getenv('USERPROFILE'), '.aws', 'credential', 'tenkal_accessKeys.csv')
aws_access_key_id = ''
aws_secret_access_key = ''

with open(aws_credentials_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        aws_access_key_id, aws_secret_access_key = row

region_name = 'us-east-1'

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=region_name)

bucket_name = 'monlam.ai.ocr'
prefix = 'Style_classification/works/manuscript_works/'

response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

image_urls = {}
work_id_count = 0

for obj in response.get('Contents', []):
    key = obj['Key']
    if '/' in key:
        key_parts = key.split('/')
        if len(key_parts) >= 5:
            work_id = key_parts[3]
            if work_id not in image_urls:
                image_urls[work_id] = []
                work_id_count += 1 
            image_urls[work_id].append({
                'name': f'{work_id}_{key_parts[-1]}',
                'imageUrl': f'https://s3.amazonaws.com/{bucket_name}/{key}'
            })
        else:
            print(
                f"Key '{key}' do not have 5 parts.")

selected_images = {}
for work_id, urls in image_urls.items():
    random.shuffle(urls) 
    selected_images[work_id] = urls[:3]  

json_data = []
for urls in selected_images.values():
    json_data.extend(urls)

file_path = '../../data/json/sample_images.json'

with open(file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=2)

print(f'json saved at: {file_path}')
print(f'work_ids processed: {work_id_count}')
