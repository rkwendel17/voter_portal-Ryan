import os

from app import create_app
from seed import seed

# Warning: Running this will erase the current contents of your
# database and replace it with the contents of seed.py

app = create_app()

with app.app_context():
    from project.models import db

    if os.environ["FLASK_ENV"] == "development":
        response = input(
            "Warning: Running this will erase "
            "the current contents of your database "
            "and replace it with the contents "
            "of seed.py (Y/y to confirm): "
        ).lower()

    if os.environ["FLASK_ENV"] == "test" or response == "y":
        db.drop_all()

        db.create_all()

        seed(db)
        print("Database successfully configured and seeded")

    else:
        print("Database configuration canceled")
