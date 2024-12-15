import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
)

def f1():
    logger.warning("Pas bien!")
    logger.info("Le ciel est blanc")

f1()