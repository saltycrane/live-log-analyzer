import logging
import sys

ERROR_LOG_FILENAME = 'lla-error.log'

# set up formatting
stdout_formatter = logging.Formatter('%(message)s')
formatter = logging.Formatter(
    '[%(asctime)s] %(levelno)s (%(process)d) %(module)s: %(message)s')

# set up logging to STDOUT for all levels DEBUG and higher
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(stdout_formatter)

# set up logging to a file for all levels WARNING and higher
fh2 = logging.FileHandler(ERROR_LOG_FILENAME)
fh2.setLevel(logging.WARN)
fh2.setFormatter(formatter)

# create Logger object
mylogger = logging.getLogger('MyLogger')
mylogger.setLevel(logging.DEBUG)
mylogger.addHandler(sh)
mylogger.addHandler(fh2)

# create shortcut functions
debug = mylogger.debug
info = mylogger.info
warning = mylogger.warning
error = mylogger.error
critical = mylogger.critical
