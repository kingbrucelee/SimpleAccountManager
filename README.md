Database library used : SQLAlchemy which is database system agnostic.
Database system choosen : SQLite3
Hashing Algorithm : Argon2
Language : Flask (Python) with BootStrap CSS frontend
# Info
SQLAlchemy requires a secret key which is set to be read from enviroment variables using environ.get('DATABASE_KEY', 'obraz_szklanka_szafa') from os module. If not found it falls back to a static "obraz_szklanka_szafa".
It is also used a passkey to access admin_panel. (Create cookie named "admin" with value equal to it)

# Functionality
Account: Login, Create, Delete, Change + Admin Routes
Course : Create, Delete, Join
Task : Create, Delete, Submit, ViewSubmission, GradeSubmission
Supports file upload and checking date of submission

Minimalistic UI
