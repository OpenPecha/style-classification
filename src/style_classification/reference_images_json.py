import os
import json
from config import get_s3_client

def upload_files_to_s3(local_folder, bucket_name, folder_name):
    s3 = get_s3_client()
    all_files = [os.path.join(local_folder, f) for f in os.listdir(local_folder) if os.path.isfile(os.path.join(local_folder, f))]

    json_data = []
    for file_path in all_files:
        relative_path = os.path.relpath(file_path, local_folder)
        file_name = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, f'{folder_name}/reference_images/{relative_path}')

        name_without_extension = os.path.splitext(file_name)[0]  
        json_data.append({
            'name': name_without_extension,  
            'imageUrl': f'https://s3.amazonaws.com/{bucket_name}/{folder_name}/reference_images/{relative_path}'
        })

    return json_data

def save_json_file(json_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=2, ensure_ascii=False)

def main():
    bucket_name = 'monlam.ai.ocr'
    folder_name = 'Style_classification'
    local_folder ='../../data/reference_images'

    json_data = upload_files_to_s3(local_folder, bucket_name, folder_name)

    json_file_path = '../../data/json/reference_images.json'
    save_json_file(json_data, json_file_path)

if __name__ == "__main__":
    main()
