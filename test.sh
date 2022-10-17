export APPLICATION_SETTINGS=config_test.py

export FLASK_APP=app
export FLASK_ENV=test
pipenv run python db_create.py # Create db from scratch in sqllite each time for testing
pipenv run python -m pytest --cache-clear $1
