import csv
import ast
def initialize_tests_db(csv_file_path: str) -> list:
    """
    Initialize tests database from a CSV file.

    :param csv_file_path: Path to the CSV file containing tests data.
    :return: List of dictionaries representing tests data.
    """
    tests_db = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            options_list = ast.literal_eval(row['options'])  # Convert the string to a list safely
            
            test_data = {
                'id': int(row['id']),
                'question': row['question'],
                'theme': row['theme'],
                'options': options_list,
                'correct_answer': row['correct_answer']
            }

            tests_db.append(test_data)

    return tests_db

def initialize_users_db(csv_file_path: str) -> list:
    """
    Initialize users database from a CSV file.

    :param csv_file_path: Path to the CSV file containing users data.
    :return: List of dictionaries representing users data.
    """
    users_db = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            user_data = {
                'id': int(row['id']),
                'username': row['username'],
                'password': row['password'],
                'full_name': row['full_name'],
                'course': row['course'],
                'group': row['group']
            }

            users_db.append(user_data)

    return users_db