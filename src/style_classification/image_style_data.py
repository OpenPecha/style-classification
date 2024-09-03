import os
import json
import psycopg2
import pathlib
import csv


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
    query = f'SELECT category, "imageUrl" FROM "{schema_name}"."{table_name}" WHERE status = %s'
    try:
        cursor.execute(query, ('reviewed',))
        rows = cursor.fetchall()
        # Process each row to extract name and work_id
        processed_rows = []
        for category, image_url in rows:
            name = image_url.split('/')[-1]  # Extract the name from the imageUrl
            work_id = image_url.split('/')[-2]  # Extract work_id from the name
            processed_rows.append((name, work_id, category, image_url))
        return processed_rows
    except psycopg2.Error as e:
        raise Exception(f"failed to fetch images: {e}")


def save_images_to_csv(rows, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['name', 'work_id', 'category', 'imageUrl'])
        csvwriter.writerows(rows)


def main():
    json_file_path = pathlib.Path.home() / 'db_config.json'
    load_db_config(json_file_path)

    schema_name = 'public'
    table_name = 'Task'

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        rows = fetch_images(cursor, schema_name, table_name)

        output_file = 'data/style_classified_data/style_classification_3.csv'
        save_images_to_csv(rows, output_file)
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    main()
