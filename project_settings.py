import logging
import os


AUTH_TOKEN = '9bc55d8b63d24305a2f0fe0da7c67292'

AZURE_BLOB_CONTAINER_NAME = 'botcache'
AZURE_DB_PORT = '1433'
AZURE_STORAGE_BLOB_DATA_EXPIRE = '00:01:00'
ConnectionName = 'myOAuth'
MS_BOT_PORT = 3978

# day, start_hour, end_hour, start_minute, end_minute
RESET_TIME_TRIGGER = os.environ.get('RESET_TIME_TRIGGER', '6,19,20,10,30').split(',')
# day, start_hour, end_hour
SEND_TIME_TRIGGER = os.environ.get('SEND_TIME_TRIGGER', '0,7,8').split(',')
FIRED_TIME_TRIGGER = os.environ.get('SEND_TIME_TRIGGER', '6,15,16').split(',')

VIBER_AVATAR = 'https://i.postimg.cc/CL3kfH6q/viber-bot-avatar.png'
VIBER_BOT_NAME = 'Як ви? Де ви?'
VIBER_TOKEN = os.environ.get('VIBER_TOKEN', '')
VIBER_WEBHOOK = os.environ.get('VIBER_WEBHOOK', '')

MAIL_FROM = 'svc-MAIL-onboarding@metinvestholding.com'
MAIL_SERVER = 'smtp.office365.com'


REDIS_MESSAGE_LIMIT = 1000
REDIS_PORT = 6380

#  Летнее+3/зимнее+2 время, поправка на тайм-зону
TIMEZONE_DELAY = 0

# Общее для всех с секретом
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

# Разное для всех
AZURE_SQL_DB_HOST = os.environ.get('AZURE_SQL_DB_HOST', '')
AZURE_SQL_DB_NAME = os.environ.get('AZURE_SQL_DB_NAME', '')
AZURE_SQL_DB_PASSWORD = os.environ.get('AZURE_SQL_DB_PASSWORD', '')
AZURE_SQL_DB_USER = os.environ.get('AZURE_SQL_DB_USER', '')
AZURE_SQL_OBJECT_ID = os.environ.get('AZURE_SQL_OBJECT_ID', '')
AZURE_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', '')
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_KEY = os.environ.get('AZURE_STORAGE_KEY', '')

IS_LOCAL_ENV = int(os.environ.get('IS_LOCAL_ENV', 1))

MICROSOFT_AUTH_TENANT_ID = 'b0bbbc89-2041-434f-8618-bc081a1a01d4'
MICROSOFT_AUTH_CLIENT_ID = os.environ.get('MICROSOFT_AUTH_CLIENT_ID', '')
MICROSOFT_AUTH_CLIENT_SECRET = os.environ.get('MICROSOFT_AUTH_CLIENT_SECRET', '')

MicrosoftAppId = os.environ.get('MicrosoftAppId', '')
MicrosoftAppPassword = os.environ.get('MicrosoftAppPassword', '')

REDIS_DB = os.environ.get('REDIS_DB', '')

REDIS_APP_NAME = os.environ.get('REDIS_APP_NAME', '')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')

LOG_TO_FILE = int(os.environ.get('LOG_TO_FILE', '0'))

if os.environ.get('LOGGER_LEVEL') == 'DEBUG':
    LOGGER_LEVEL = logging.DEBUG
    DJANGO_LOGGER_LEVEL = 'DEBUG'
else:
    LOGGER_LEVEL = logging.INFO
    DJANGO_LOGGER_LEVEL = 'INFO'

if IS_LOCAL_ENV == 1:
    REDIS_URI = f'redis://localhost:6379/{REDIS_DB}'
    PING_FILE = 'ping.csv'
    LOG_FILE_PATH = os.path.join('logs', 'debug_logs.log')

else:
    REDIS_URI = f'rediss://:{REDIS_PASSWORD}@{REDIS_APP_NAME}.redis.cache.windows.net:{REDIS_PORT}/{REDIS_DB}'
    PING_FILE = os.path.join('/home/site/wwwroot/logs/', 'ping.csv')
    LOG_FILE_PATH = os.path.join('/home/site/wwwroot/logs/', 'debug_logs.log')
    # PING_FILE = 'ping.csv'
    # LOG_FILE_PATH = os.path.join('logs', 'debug_logs.log')

# REDIS KEYS
REDIS_MESSAGE_QUEUE_KEY = 'steps-message-queue'
REDIS_ADMIN_MAIL_QUEUE_KEY = 'admin-mail-queue'
REDIS_DIRECT_MESSAGE_QUEUE_KEY = 'direct-message-queue'  # From Django view

REDIS_MESSAGE_WORKER_HEALTH_CHECK_KEY = 'message-worker-health-check'
REDIS_ADMIN_MAIL_WORKER_HEALTH_CHECK_KEY = 'admin-mail-worker-health-check'
REDIS_DIRECT_MESSAGE_WORKER_HEALTH_CHECK_KEY = 'direct-message-worker-health-check'

REDIS_CUSTOMER_TMPL = 'customer-{}'


REDIS_CONVERSATION_REFERENCE_TMPL = 'conv-reference-{}'

REDIS_CREATED_TASK_LIST = 'created-task-list'


REDIS_OTP_TMPL = 'otp-{}'

MESSAGE_TOKEN_CACHE = list()
