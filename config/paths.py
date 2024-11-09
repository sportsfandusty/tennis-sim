from pathlib import Path

########## PATH DECLARATIONS ##########
BASE_DIR = Path(__file__).resolve().parent.parent  # Now points to '/home/ds/Desktop/broken_sports'

# ROOT LEVEL 
FUNCTIONS_DIR = BASE_DIR / 'functions'
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'  # Correct path

# FUNCTIONS DIRECTORY
TENNIS_FUNCTIONS = FUNCTIONS_DIR / 'tennis'
DATABASE_FUNCTIONS = FUNCTIONS_DIR / 'database'  # Corrected path
DRAFTKINGS_FUNCTIONS = FUNCTIONS_DIR / 'draftkings'

# DATA DIRECTORY
CSV_DIR = DATA_DIR / 'csvs'
TENNIS_DATA = DATA_DIR / 'tennis'
# TENNIS DATA SUBDIRECTORY
TENNIS_STATS = TENNIS_DATA / 'stats'
TENNIS_DB = TENNIS_DATA / 'database.db'

# Log files
FUNCTIONS_LOG = LOGS_DIR / 'functions.log'
ERRORS_LOG = LOGS_DIR / 'errors.log'
DEBUG_LOGS = {
    "database": LOGS_DIR / 'db_debug.log',
    "draftkings": LOGS_DIR / 'draftkings_debug.log',
    "tennis": LOGS_DIR / 'tennis_debug.log',
}

########## PATH DECLARATIONS ##########

