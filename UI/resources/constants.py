# -*- coding: utf-8 -*-

SAVE_PASSWORD_HASHED = True
MAX_RETRIES_DOWNLOAD_FROM_SAME_FARMER = 3
MAX_RETRIES_UPLOAD_TO_SAME_FARMER = 3
MAX_RETRIES_NEGOTIATE_CONTRACT = 1000
MAX_RETRIES_GET_FILE_POINTERS = 100
MAX_RETRIES_TOKEN_RESOLVING = 20

GET_DEFAULT_TMP_PATH_FROM_ENV_VARIABLES = True
GET_HOME_PATH_FROM_ENV_VARIABLES = True

FILE_POINTERS_REQUEST_DELAY = 1
FILE_POINTERS_ITERATION_DELAY = 0.2
CONTRACT_NEGOTIATION_ITERATION_DELAY = 0.2
MAX_POINTERS_RESOLVED_IN_ONE_PART = 50
MINIMAL_ALLOWED_BRIDGE_REQUEST_TIMEOUT = 5
# int: file pointers request delay, file pointers iteration delay, max pointers resolved in one part,
#  minimal bridge request timeout, in seconds.

MAX_DOWNLOAD_REQUEST_BLOCK_SIZE = 4 * 1024
MAX_UPLOAD_REQUEST_BLOCK_SIZE = 4096
MAX_UPLOAD_CONNECTIONS_AT_SAME_TIME = 4
MAX_DOWNLOAD_CONNECTIONS_AT_SAME_TIME = 4
CONCURRENT_UPLOADING = False

DEFAULT_MAX_BRIDGE_REQUEST_TIMEOUT = 90
DEFAULT_MAX_FARMER_CONNECTION_TIMEOUT = 7
DEFAULT_MAX_FARMER_DOWNLOAD_READ_TIMEOUT = 17
# int: maximum bridge request timeout, in seconds.

MAX_ALLOWED_UPLOAD_CONCURRENCY = 9999
MAX_ALLOWED_DOWNLOAD_CONCURRENCY = 9999


DEFAULT_BRIDGE_API_URL = 'api.storj.io'
CONFIG_FILE_NAME = 'storj_client_config.xml'

# DESIGN
DISPLAY_FILE_CREATION_DATE_IN_MAIN = True
DISPLAY_FILE_ID_IN_MAIN = True
FILE_LIST_SORTING_MAIN_ENABLED = True
AUTO_SCROLL_UPLOAD_DOWNLOAD_QUEUE = True
SHOW_TRAY_ICON = False
BUCKETS_LIST_SORTING_ENABLED = True
MIRRORS_TREE_SORTING_ENABLED = True
FIXED_WINDOWS_SIZE = True
ALLOW_DOWNLOAD_FARMER_POINTER_CANCEL_BY_USER = True
ALLOW_UPLOAD_FARMER_CANCEL_BY_USER = True
DATA_TABLE_EDIT_ENABLED = False

# BLACKLISTING
FARMER_NODES_EXCLUSION_FOR_UPLOAD_ENABLED = True
FARMER_NODES_EXCLUSION_FOR_DOWNLOAD_ENABLED = True
BLACKLIST_MAX_LENGTH = 300
BLACKLISTING_MODE = 2
# 1 - blacklist all farmers to which shard have been recently uploaded
# 2 - blacklist only farmers to which transfer failed

# PATHS
USE_USER_ENV_PATH_FOR_TEMP = False
DEFAULT_ENCRYPTION_KEYS_DIRECTORY = ""

# SHARDING
DEFAULT_MAX_SHARD_SIZE = 4294967296  # 4Gb
DEFAULT_SHARD_SIZE = 2 * (1024 * 1024)  # 8Mb

# UPLOAD
REED_SOLOMON_ENCODING_ENABLED = True
