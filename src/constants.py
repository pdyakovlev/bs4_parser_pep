from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
DOWNLOADS_DIR = BASE_DIR / 'downloads'
RESULTS_DIR = BASE_DIR / 'results'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOGS_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
PEP_BASE_URL = "https://peps.python.org/"
EXPECTED_STATUS = {"Status": "Status"}
PRETTY = 'pretty'
FILE = 'file'
