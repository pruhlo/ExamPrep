import ast
import csv
from typing import Dict, List, Tuple, Union, Optional
from datetime import datetime, timedelta
import json
import jwt
import logging
import random
from fastapi import (
    Depends, 
    FastAPI, 
    Form, 
    HTTPException, 
    Query, 
    Request, 
    Response, 
    status
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
import secrets

# Import initialization functions for databases
from initialize_databases import initialize_tests_db, initialize_users_db
from tests_DB.tools import *
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key and algorithm for JWT
your_secret_key = secrets.token_urlsafe(32)
SECRET_KEY = your_secret_key
ALGORITHM = "HS256"

# Initialize FastAPI app
app = FastAPI()

# Configure testing time
testing_time = 30
num_tests = 10

# HTML templates
templates = Jinja2Templates(directory="templates")

# Dependency for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Paths to CSV files
csv_file_path_tests = 'tests_database.csv'
csv_file_path_users = 'users_database.csv'

# Create tests_database.csv
folder_path = "tests_DB/"
result = get_txt_files(folder_path)
name_files = []
for name in result:
    name_files.append(folder_path+name)
csv_file_path = 'tests_database.csv'
create_csv_from_files(name_files, csv_file_path)

# Initialize databases
tests_db = initialize_tests_db(csv_file_path_tests)
users_db = initialize_users_db(csv_file_path_users)


# Dependency to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Union[str, int]]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Ensure that the token is encoded as bytes
        token_bytes = token.encode("utf-8")

        # Attempt to decode the token and get user data
        payload = jwt.decode(token_bytes, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise credentials_exception
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise credentials_exception

    current_user = {"username": username, "user_id": user_id}
    return current_user


# Endpoint for welcome page
@app.get("/")
async def welcome_page(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


# Endpoint for login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, lang: str = Query(...)):
    return templates.TemplateResponse("login.html", {"request": request, 'lang': lang})


# Function to generate a token
def token_generation_function(user: Dict[str, Union[str, int]]) -> str:
    """
    Generate a token based on user data.

    :param user: Dictionary with user data (username, id).
    :return: Generated token.
    """
    data = {"sub": user["username"], "user_id": user["id"], "exp": datetime.utcnow() + timedelta(seconds=testing_time*num_tests+60)}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Endpoint to handle login
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), lang: str=Form(...),response: Response = None):
    user = None
    for u in users_db:
        if u["username"] == username and u["password"] == password:
            user = u
    if user is None:
        if lang == 'uk':
            error_message = "Недійсні облікові дані. Перевірте введене ім'я користувача або пароль."
        else:
            error_message = "Invalid credentials. Please check your username or password."
        if response is None:
            response = Response(status_code=303)
        response = RedirectResponse(url=f"/login?lang={lang}&error={error_message}", status_code=303)
        return response
    token = token_generation_function(user)
    headers = {"Authorization": f"{token}"} # problems with transport token to headers into (on at) testing page
    response = RedirectResponse(url=f"/testing?lang={lang}&token={token}", status_code=303, headers=headers)
    return response

# Endpoint for the testing page
@app.get("/testing")
async def get_testing_page(request: Request, token: str = Query(...), lang: str = Query(...)):
    current_user = get_current_user(token)
    unique_themes = set(test["theme"] for test in tests_db)
    unique_themes_list = list(unique_themes)
    return templates.TemplateResponse(
        "testing.html",
        {"request": request, "user": current_user, "themes": unique_themes_list, 
         "token": token, 'lang': lang, "num_tests":num_tests}
    )


# Endpoint to start a test
# @app.get("/start_test", response_class=HTMLResponse)
# async def start_test(request: Request, theme: str = Form(...), token: str = Query(...), num_tests: int = Form(...)):
#     current_user = get_current_user(token)
#     filtered_tests = [test for test in tests_db if test["theme"] == theme]
#     selected_tests = filtered_tests[:num_tests]

#     return templates.TemplateResponse(
#         "start_test.html",
#         {"request": request, "user": current_user, "tests": selected_tests, "theme": theme, 'testing_time': testing_time}
#     )


# Endpoint to get the jQuery script
@app.get('/jquery-3.6.4.min.js')
async def get_jquery():
    with open('templates/jquery-3.6.4.min.js', 'r') as f:
        jq = f.read()
    return Response(content=jq, media_type='application/javascript')


# Alternative implementation for starting a test
# Endpoint to start a test
@app.post("/start_test")
async def start_test(request: Request, theme: str = Form(...), token: str = Query(...), num_tests: int = Form(...), lang: str=Form(...)):
    current_user = get_current_user(token)
    theme_tests = [test for test in tests_db if test["theme"] == theme]
    for test in theme_tests:
        random.shuffle(test['options'])
    _num_tests = min(abs(num_tests), len(theme_tests))
    if num_tests == 0:
        num_tests = 10
    selected_tests = random.sample(theme_tests, _num_tests)
    if lang =='en':
        submit = 'Submit Test'
        Time_Remaining = 'Time Remaining: '
        seconds = ' seconds'
    else:
        submit = 'Надіслати тест'
        Time_Remaining = 'Час, що залишився: '
        seconds = ' секунд'

    return templates.TemplateResponse(
        "start_test.html",
        {"request": request, "token": token, "user": current_user,
        "tests": selected_tests,
        "theme": theme,
        'testing_time': testing_time * num_tests,
        'submit':submit,
        'Time_Remaining':Time_Remaining,
        'seconds':seconds,
        'lang':lang
    })


# Endpoint to submit a test
@app.post("/submit_test")
async def submit_test(request: Request, testData: str = Form(...), token: str = Form(...), lang: str=Form(...)):
    global tests_db
    data = json.loads(testData)
    user_ip = request.client.host
    current_user = get_current_user(token)
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    current_time = now.strftime("%H:%M:%S")
    score = 0
    n_test = 0
    questions = []
    for d in data:
        n_test += 1
        test_id = int(d['id'])
        matching_tests = [test for test in tests_db if int(test['id']) == test_id]

        if not matching_tests:
            raise HTTPException(status_code=400, detail=f"Test with ID {test_id} not found")

        matching_test = matching_tests[0]
        matching_test.update(d)
        matching_test.update(current_user)
        matching_test.update({"date": current_date, "time": current_time,"user_ip":user_ip})

        questions.append(matching_test)

        if matching_test['correct_answer'] == d['answer']:
            score += 1

    if n_test == 0:
        score = 0
        total_score = 0
    else:
        total_score = f'{score / num_tests * 100:.2f} %'
        score = f'{score / n_test * 100:.2f} %'
        

    filename = 'results_database.csv'

    try:
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = questions[0].keys()  # Get field names from the first data item
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not csvfile.tell():  # If file is empty, write the header
                writer.writeheader()

            writer.writerows(questions)
    except IndexError:
        pass
        
    return templates.TemplateResponse(
        "result_test.html",
        {"request": request, "user": current_user, "len_tests": n_test, 
         "questions": questions, "score": score, "total_score":total_score, 'lang':lang}
    )
