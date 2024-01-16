# 1. Open a terminal or command prompt:

	On Windows, you can use Command Prompt or PowerShell.
	On macOS or Linux, you can use the terminal.

# 2. Navigate to the desired directory:

	Use the cd command to change the directory to where you want to create your virtual environment.
```bash
cd path/to/your/directory
```

# 3. Create a virtual environment:
	Run the following command to create a virtual environment. You can replace myenv with the desired name for your virtual environment.
```bash
python3 -m venv myenv
```
# 4. Activate the virtual environment:
	On Windows, run:
```bash
myenv\Scripts\activate
```
	On macOS or Linux, run:
```bash
source myenv/bin/activate
```

# 5. Install requirements from requirements.txt
```bash
pip install -r requirements.txt

```

# 6. Run application:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 11008
```
# 7. Create docker image
docker build -t testing_app .

# 8. Run docker container from image
```bash
docker run -p 11008:11008 testing_app
```