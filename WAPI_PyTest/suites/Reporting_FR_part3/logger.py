#Logging.
import logging
import logging.handlers
LOG_FILENAME='reporting.log'
logger = logging.getLogger('reporting')
logger.setLevel(logging.DEBUG)
#fh=logging.FileHandler(LOG_FILENAME)
fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=21000000, backupCount=5)
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
