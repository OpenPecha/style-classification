import random
import json
from config import get_s3_client

s3 = get_s3_client()
bucket_name = 'monlam.ai.ocr'
prefix = 'Style_classification/works/manuscript_works/'

image_urls = {}
work_id_count = 0
continuation_token = None

while True:
    if continuation_token:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, ContinuationToken=continuation_token)
    else:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    for obj in response.get('Contents', []):
        key = obj['Key']
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
            print(f"Key '{key}' does not have 5 parts.")

    if response.get('IsTruncated'):
        continuation_token = response['NextContinuationToken']
    else:
        break


selected_images = {}
for work_id, urls in image_urls.items():
    random.shuffle(urls)
    selected_images[work_id] = urls[:3]

selected_image_count = sum(len(urls) for urls in selected_images.values())
print(f'total images: {selected_image_count}')

json_data = []
for urls in selected_images.values():
    json_data.extend(urls)

file_path = '../../data/json/sample_images.json'
with open(file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=2)

print(f'json saved at: {file_path}')
print(f'work_ids processed: {work_id_count}')
