import os

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, 'data')
TEST_DATA_DIR = os.path.join(DIR, 'tests', 'test_data')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

DB_NAME = 'dog_walker.db'
DATABASE = os.path.join(DATA_DIR, DB_NAME)
TEST_DATABASE = os.path.join(TEST_DATA_DIR, DB_NAME)
FLAG_TABLE = 'flags'
EMAIL_CONFIG = os.path.join(DATA_DIR, '.email_config.json')

RUNNER_TIMEOUT = 60 * 60 * 1  # every hour
FLAG_TIMEOUT = 60 * 60 * 24 # every day
