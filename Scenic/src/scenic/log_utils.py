import json
import logging
import os


def setup_logging(log_type_name):
    log_directory = "/home/recording/log_files"
    log_filename = log_type_name
    full_log_path = os.path.join(log_directory, log_filename)

    # Create log directory if it does not exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logging.basicConfig(
        filename=full_log_path,
        filemode="w",  # Change to 'a' to append to the log file
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

def setup_logging_expanded(log_type_name):
    log_directory = "/home/recording/log_files_expanded"
    log_filename = f"{log_type_name}.log"
    full_log_path = os.path.join(log_directory, log_filename)

    # Create log directory if it does not exist
    os.makedirs(log_directory, exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger(log_type_name)
    logger.setLevel(logging.INFO)

    # Create handlers
    file_handler = logging.FileHandler(full_log_path)
    file_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)

    return logger

# Utility function to log detailed information
def log_detailed_info(logger, info_dict):
    """
    Logs detailed information including both known and detected attributes.

    Args:
        logger: The logging object.
        info_dict (dict): Dictionary containing all the information to log.
    """
    logger.info(json.dumps(info_dict))