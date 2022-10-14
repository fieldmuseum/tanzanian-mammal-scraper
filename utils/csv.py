'''Utility functions for working with CSVs'''
import csv, os

def get_column_from_csv(file: str, has_headers=True, column=0) -> list:
    '''Returns row data, for a particular column, from a CSV file'''
    '''column parameter is zero indexed'''
    with open(file, encoding='utf-8', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        if has_headers: next(reader) # skip first line if there are headings
        data = []
        for row in reader:
            data.append(row[column])

    return data

def rows(file: str) -> list:
    '''Returns a list of rows (dicts) from an input CSV file'''
    rows = []
    with open(file, encoding='utf-8', mode = 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for r in reader: rows.append(r)
    return rows


def output_list_of_dict_to_csv(list_of_dict: list, csv_fieldnames: list, output_path: str, output_file: str):
    '''Output a list of dictionaries as a CSV, with keys as headers'''

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # today = datetime.date.today()
    # today = today.strftime("%Y-%m-%d")

    print(output_path + '/' + output_file)

    if len(list_of_dict) > 0:
        with open(output_path + '/' + output_file, encoding='utf-8', mode='w') as missed_media_output:
            write = csv.DictWriter(missed_media_output, fieldnames=csv_fieldnames)
            write.writeheader()
            write.writerows(list_of_dict)