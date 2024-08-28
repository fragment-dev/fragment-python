import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

console_log = logging.getLogger("console")
