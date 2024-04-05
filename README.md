# SimpleAccountManager
This is work in progress web app for student project. Currently it allows for creation, deletion, edition and logging in. I

# Info
SQLAlchemy requires a secret key which is set to be read from enviroment variables using environ.get('DATABASE_KEY', 'obraz_szklanka_szafa') from os module. If not found it falls back to a static "obraz_szklanka_szafa".