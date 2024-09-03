import csv
import os
import pathlib

def classify_and_save_csv(input_file, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Paths for classified CSV files
    manuscript_output_file = os.path.join(output_dir, 'manuscript_works.csv')
    woodblock_output_file = os.path.join(output_dir, 'woodblock_works.csv')
    
    # Open the input file and classify rows
    with open(input_file, 'r', newline='') as csvfile:
        csvreader = csv.DictReader(csvfile)
        
        # Open the output files for classified data
        with open(manuscript_output_file, 'w', newline='') as manuscript_csvfile, \
             open(woodblock_output_file, 'w', newline='') as woodblock_csvfile:
            
            manuscript_writer = csv.DictWriter(manuscript_csvfile, fieldnames=csvreader.fieldnames)
            woodblock_writer = csv.DictWriter(woodblock_csvfile, fieldnames=csvreader.fieldnames)
            
            # Write headers to the output files
            manuscript_writer.writeheader()
            woodblock_writer.writeheader()
            
            # Classify each row and write to the appropriate file
            for row in csvreader:
                if 'manuscript_works' in row['imageUrl']:
                    manuscript_writer.writerow(row)
                elif 'woodblock_works' in row['imageUrl']:
                    woodblock_writer.writerow(row)
    
    print(f"Classification complete. Files saved in {output_dir}")

def main():
    input_file = 'data/style_classified_data/style_classification_3.csv'
    output_dir = 'data/style_classified_data/classified'
    
    classify_and_save_csv(input_file, output_dir)

if __name__ == "__main__":
    main()
