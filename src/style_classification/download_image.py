import os
import json
import psycopg2
import pathlib
import requests
from concurrent.futures import ThreadPoolExecutor


def load_db_config(config_file):
    with open(config_file, 'r') as f:
        db_config = json.load(f)
        for key, value in db_config.items():
            os.environ[key] = value


def connect_to_db():
    db_params = {
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '5432')
    }

    missing_params = [key for key, value in db_params.items() if value is None]
    if missing_params:
        raise EnvironmentError(f"environment var not set: {', '.join(missing_params)}")

    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        raise Exception(f"db connection failed: {e}")


def fetch_images(cursor, schema_name, table_name):
    query = f'SELECT "imageUrl", category, name FROM "{schema_name}"."{table_name}" WHERE status = %s'
    try:
        cursor.execute(query, ('reviewed',))
        return cursor.fetchall()
    except psycopg2.Error as e:
        raise Exception(f"failed to fetch images: {e}")


def download_image(image_data):
    image_url, image_name, category_dir = image_data
    try:
        print(f"downloading image {image_name} to {category_dir}")
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(category_dir, image_name), 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
    except Exception as e:
        print(f"failed to download {image_url}: {e}")


def save_images(rows, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    image_data_list = []
    for row in rows:
        image_url, category, image_name = row
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        image_data_list.append((image_url, category, image_name, category_dir))

    with ThreadPoolExecutor() as executor:
        executor.map(download_image, image_data_list)


def main():
    json_file_path = pathlib.Path.home() / 'db_config.json'
    load_db_config(json_file_path)

    schema_name = 'public'
    table_name = 'Task'

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        rows = fetch_images(cursor, schema_name, table_name)

        output_dir = '../../data/classified_images'
        save_images(rows, output_dir)
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    main()
