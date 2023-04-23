# UBUNTU RUN
# Local Setup in Ubuntu
    - Clone the project
    - Run `local_setup.sh`

# Local Development Run in Ubuntu
    - `local_run.sh` It will start the flask app in `production`. Suited for local development


# WINDOWS RUN
- Clone the project
- Run `pip install -r requirements.txt`
- Run `python main.py`


# Replit run
- Clone the project
- Go to shell and run
    `pip install -r requirements.txt`
- Click on `main.py` and click button run


# Folder Structure

- `db_directory` has the sqlite DB. It can be anywhere on the machine. Adjust the path in ``application/config.py`. Repo ships with one required for testing.
- `application` is where our application code is.
- `local_setup.sh` set up the virtualenv inside a local `.env` folder. Uses `pyproject.toml` and `poetry` to setup the project
- `local_run.sh`  Used to run the flask application.
- `static` - default `static` files folder. It serves at '/static' path. More about it is [here](https://flask.palletsprojects.com/en/2.0.x/tutorial/static/).

- `templates` - Default flask templates folder


```
├── application
|   ├── api.py
│   ├── config.py
│   ├── controllers.py
│   ├── database.py
│   ├── __init__.py
│   ├── models.py
|   ├── script.py
│   └── __pycache__

├── db_directory
│   └── kb.sqlite3
├── static
├── templates
├── api.yaml
├── local_run.sh
├── local_setup.sh
├── main.py
├── readme.md
├── requirements.txt

```# Kanban-board-App
