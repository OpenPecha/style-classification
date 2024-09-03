import random
import json
from config import get_s3_client


def get_image_urls(bucket_name, prefix):
    s3 = get_s3_client()
    image_urls = {}
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

    return image_urls


def select_random_images(image_urls):
    selected_images = {}
    for work_id, urls in image_urls.items():
        random.shuffle(urls)
        selected_images[work_id] = urls[:3]
    return selected_images


def save_json_data(selected_images, file_paths):
    json_data = []
    for urls in selected_images.values():
        json_data.extend(urls)

    total_items = len(json_data)
    half_size = total_items // 2
    remainder = total_items % 2
    start_idx = 0
    image_counts = []
    for i in range(2):
        end_idx = start_idx + half_size
        if remainder > 0:
            end_idx += 1
            remainder -= 1

        batch_data = json_data[start_idx:end_idx]
        image_counts.append(len(batch_data))
        with open(file_paths[i], 'w') as json_file:
            json.dump(batch_data, json_file, indent=2)
        print(f'JSON saved at: {file_paths[i]}')

        start_idx = end_idx

    return image_counts


def main():
    bucket_name = 'monlam.ai.ocr'
    prefix = 'Style_classification/works/woodblock_works/'

    image_urls = get_image_urls(bucket_name, prefix)
    selected_images = select_random_images(image_urls)
    selected_image_count = sum(len(urls) for urls in selected_images.values())
    print(f'total images: {selected_image_count}')

    file_path_1 = '../../data/json/woodblock/woodblock_sample_images_batch1.json'
    file_path_2 = '../../data/json/woodblock/woodblock_sample_images_batch2.json'
    image_counts = save_json_data(selected_images, [file_path_1, file_path_2])

    for i, count in enumerate(image_counts, start=1):
        print(f'Batch {i}: {count} images')


if __name__ == "__main__":
    main()
