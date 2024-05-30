import os
import json
from config import get_s3_client

s3 = get_s3_client()
bucket_name = 'monlam.ai.ocr'
folder_name = 'Style_classification'
local_folder ='../../data/reference_images'

all_files = [os.path.join(local_folder, f) for f in os.listdir(local_folder) if os.path.isfile(os.path.join(local_folder, f))]

json_data = []
for file_path in all_files:
    relative_path = os.path.relpath(file_path, local_folder)
    file_name = os.path.basename(file_path)
    s3.upload_file(file_path, bucket_name, f'{folder_name}/reference_images/{relative_path}')

    json_data.append({
        'name': file_name,
        'imageUrl': f'https://s3.amazonaws.com/{bucket_name}/{folder_name}/reference_images/{relative_path}'
    })

json_file_path = '../../data/json/reference_images.json'

with open(json_file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=2)
