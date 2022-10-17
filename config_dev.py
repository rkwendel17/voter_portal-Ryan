SQLALCHEMY_TRACK_MODIFICATIONS = False

# This secret key is used to secure sessions, which allow Flask to remember information from one request to another
# the secret key should be a long random string.
# View documentation later: https://flask.palletsprojects.com/en/1.1.x/api/#sessions
# Key chosen via: https://randomkeygen.com/
SECRET_KEY = "lH4pzHO4Mqc2q01gW0HuUeUkhEoKw8lw"

EMAIL = "Voter.portal.fse@gmail.com"

from config_secret import API_KEY, SQLALCHEMY_DATABASE_URI
