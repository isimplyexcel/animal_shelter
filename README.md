# animal_shelter_flask_app

## Project Quickstart

* Before you start your app, make sure you have database.py file under animal_shelter folder. This file should **NEVER** be pushed to remote; it contains mysql database credentials.
* If you have any files that should not be pushed to github, add it to `.gitignore`.

- `git pull` latest master.
- Create your virtual environment by running: `python3 -m venv env`
    - This step only needs to be done once per project
- Activate your virtual env: `source env/bin/activate`
- Install packages inside virtual environment: `pip3 install -r requirements.txt`
    - If you added a new package to the project, make sure to add it to `requirements.txt`!!
-Set the `FLASK_APP` environment variable
    - Unix:
    - `export FLASK_APP=application`
    - `flask run`
    - Windows:
    - `set FLASK_APP=application`
    - `flask run`
- Open your browser and navigate to `http://0.0.0.0:33507/` to see the app in action.
- Deactivate your virtual environment when you are done: `deactivate`

### Collaborators (alphabetical order):
* Beth Myre - BethMyre
* Paul Min - isimplyexcel
