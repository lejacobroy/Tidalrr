import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
DB_PATH = os.path.join(ROOT_DIR, '../config/database.db')
SCHEMA_PATH = os.path.join(ROOT_DIR, '../config/schema.sql')
URLS_TXT_PATH = os.path.join(ROOT_DIR, '../import/urls.txt')
print(DB_PATH)