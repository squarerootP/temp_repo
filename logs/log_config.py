import logging


def setup_logger(log_name: str):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # Prevent duplicate handlers
        handler = logging.FileHandler(f"logs/{log_name}.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger