# VoterPortal

![pytest](https://github.com/kian-weimer/voter_portal/actions/workflows/pytest.yml/badge.svg)
![Push Gitlab](https://github.com/kian-weimer/voter_portal/actions/workflows/gitlab.yml/badge.svg)
![Coverage](https://github.com/kian-weimer/voter_portal/actions/workflows/python-package.yml/badge.svg)

### Start the application

    $ pipenv install  # run when updates from main affect the Pipfile or Pipfile.lock
    $ pipenv shell  # activate the virtual environment
    $ ./start.sh  # run the shell script

### Run tests

    $ pipenv install  # run when updates from main affect the Pipfile or Pipfile.lock
    $ pipenv shell  # activate the virtual environment
    $ ./test.sh  # run the shell script

## Database

### Start database server (mac with homebrew)

    $ brew services start mysql

### Stop database server (mac with homebrew)

    $ brew services stop mysql

### Restart database server (mac with homebrew)

    $ brew services restart mysql

### Initialize database (after creating new models)

    $ cd voterportal_root_directory
    $ pipenv install
    $ pipenv shell
    $ ./configure_db

## Sonarqube

### Tutorial URL

https://clas.uiowa.edu/linux/linux-services/sonarqube

### Results Portal

https://sonarqube.cs.uiowa.edu/

## Using pipenv to manage your virtual environment (instructions written for mac)

Note: You can link your pipenv environment with an ide like Pycharm  
The pipenv Python interpreter is stored in `~/.local/share/virtualenvs`  
Never install packages through the IDE, still use the pipenv command in the terminal (fact check this)
###Link with more information
https://realpython.com/pipenv-guide/#pipenv-introduction

### Install pipenv locally

In your source code root directory:

    $ pip install pipenv

### Activating the virtual environment

In your source code root directory:

    $ pipenv shell

### lock environment (do this before committing)

    $ pipenv lock

### Deactivating the virtual environment

Do this when you woul dlike to leave the virtual environment:

    $ deactivate

### Updating the virtual environment

This will download any new dependancies added in version controll.

    $ pipenv install

### Install a new package

Use this to install new packages. This will update the Pipenv file for version control.

    $ pipenv install <package_name>
