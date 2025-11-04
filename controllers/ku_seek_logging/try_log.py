from custom_logger import get_logger


logger = get_logger("KU_SEEK_LOGGER_DEV")

logger.info("No user logging")
logger.info("User logging", user="64")


def very_long_func_name_trust_me_its_long_as_fuck():
    logger.info("Very long func")
    logger.info("Very long func and User logging", user="64")


def other_funcs():
    logger.debug("Debug yea")
    logger.warning("Error bitch")
    logger.error("Shi blew up. this guy did it.", user='911')

very_long_func_name_trust_me_its_long_as_fuck()
other_funcs()