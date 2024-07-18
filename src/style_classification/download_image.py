import os
import json
import psycopg2
import pathlib
import requests


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
        raise EnvironmentError(f"env var not set: {', '.join(missing_params)}")

    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        raise


def fetch_table_schema(cursor, schema_name, table_name):
    try:
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
        """)
        return cursor.fetchall()
    except psycopg2.Error as e:
        raise


def fetch_images(cursor, schema_name, table_name):
    try:
        cursor.execute(f'SELECT id, "imageUrl", category, name FROM "{schema_name}"."{table_name}" WHERE status = %s', ('reviewed',))
        return cursor.fetchall()
    except psycopg2.Error as e:
        raise


def download_image(image_url, save_path, image_name):
    try:
        print(f"downloading image {image_name} to {save_path}")
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
    except Exception as e:
        raise


def save_images(rows, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for row in rows:
        image_id, image_url, category, image_name = row  

        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        image_path = os.path.join(category_dir, f'{image_name}.jpg')
        download_image(image_url, image_path, image_name)


def main():
    json_file_path = pathlib.Path.home() / 'db_config.json'
    load_db_config(json_file_path)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        table_name = os.getenv('DB_TABLE_NAME')
        schema_name = 'public'
        fetch_table_schema(cursor, schema_name, table_name)

        rows = fetch_images(cursor, schema_name, table_name)

        output_dir = '../../data/classified_images'
        save_images(rows, output_dir)

    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    main()
