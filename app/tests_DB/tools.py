import re
import ast
import pprint
from typing import Dict, List, Tuple
import random
import csv
import os

def clear_questions(question_text: str) -> str:
    """Clears the provided question text.

    Args:
        question_text (str): The original text of the question.

    Returns:
        str: The cleared text of the question.
    """
    return ' '.join(question_text.replace('\n', '').split('.')[1:]).strip()

def clear_answers(answer_text: str) -> Dict[str, List[str]]:
    """Clears the provided answer text and separates correct and other answers.

    Args:
        answer_text (str): The original text of the answers.

    Returns:
        Dict[str, List[str]]: A dictionary containing two lists -
            'correct_answer' for correct answers and 'other_answer' for other answers.
    """
    answers = [item for item in answer_text.split('\n') if item.strip()]
    answers_dict = {'correct_answer': [], 'other_answer': []}
    new_list_answers = []

    for answer in answers:
        if '*' not in answer:
            new_list_answers.append(' '.join(answer.split()[1:]).strip())
        elif '*' in answer:
            answers_dict['correct_answer'].append(' '.join(answer.split('*')[1:]).strip())

    answers_dict['other_answer'] = new_list_answers

    return answers_dict

def add_alphabet_letter(lines: List[List[str]]) -> List[List[str]]:
    """Adds alphabet letters to each line in a list of lines.

    Args:
        lines (List[List[str]]): List of lines to process.

    Returns:
        List[List[str]]: List of lines with alphabet letters added.
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    results = []
    for answers in lines:
        result = []
        for letter_index, line in enumerate(answers):
            letter = alphabet[letter_index]
            result.append(f"{letter}. {line}")
        results.append(result)
    return results

def remove_text_before_first_period(text: str) -> str:
    """Removes text before the first period in the provided text.

    Args:
        text (str): The input text.

    Returns:
        str: The text after the first period, stripped and with certain characters removed.
    """
    first_period_index = text.find('.')

    if first_period_index != -1:
        return text[first_period_index + 1:].strip().replace('[','').replace(']','').replace("'", '')
    else:
        return text.replace('[','').replace(']','')

    
def get_variants(data: Dict[str, Dict[str, List[str]]]) -> Tuple[List[str], List[List[str]]]:
    """Generates shuffled questions and their corresponding answer variants.

    Args:
        data (Dict[str, Dict[str, List[str]]]): Dictionary containing questions and answers.

    Returns:
        Tuple[List[str], List[List[str]]]: Shuffled questions and corresponding answer variants.
    """
    questions = list(data.keys())
    random.shuffle(questions)
    all_answers = []

    for question in questions:
        try:
            answers = []
            answers.extend(data[question]['other_answer'])
            answers.extend(data[question]['correct_answer'])  # Use extend instead of wrapping in a list
            random.shuffle(answers)
            all_answers.append(answers)
        except KeyError:
            print(f"Error: Missing data for question - {question}")

    answers = add_alphabet_letter(all_answers)

    if len(questions) == len(answers):
        return questions, answers
    else:
        raise ValueError("Number of questions does not match the number of answer variants.")    

name_files = ['під тиском.txt', 'очні.txt',]
csv_file_path = 'tests_database.csv'


def create_csv_from_files(name_files: List[str], csv_file_path: str) -> None:
    """Reads data from text files and creates a CSV file with formatted content.

    Args:
        name_files (List[str]): List of input text file names.
        csv_file_path (str): Path to the output CSV file.
    """
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['id', 'question', 'theme', 'options', 'correct_answer']
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            question_id = 1
            for name_file in name_files:
                data = {}
                with open(name_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                questions = re.findall(r'#(.*?)@', text, re.DOTALL)
                answers = re.findall(r'@(.*?)#', text, re.DOTALL)

                if len(questions) == len(answers):
                    for n, question_text in enumerate(questions):
                        q = clear_questions(question_text)
                        a = clear_answers(answers[n])
                        data[q] = a

                for key in data.keys():
                    options = data[key]['other_answer'] + data[key]['correct_answer']
                    csv_writer.writerow({
                        'id': str(question_id),
                        'question': key,
                        'theme': f'{name_file[9:-4]}',
                        'options': f'{options}',
                        'correct_answer': data[key]['correct_answer'][0],
                    })
                    question_id += 1
    except IndexError:
        print(name_file)
        print(key)

    print(f'CSV file created successfully: {csv_file_path}')

def get_txt_files(folder_path):
    files = os.listdir(folder_path)
    txt_files = [file for file in files if file.endswith(".txt")]
    return txt_files

if __name__ == "__main__":
    import numpy as np
    folder_path = "tests_DB/"
    result = get_txt_files(folder_path)
    name_files = []
    for name in result:
        name_files.append(folder_path+name)
    csv_file_path = 'tests_database.csv'
    create_csv_from_files(name_files, csv_file_path)
    

