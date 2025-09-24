#logging_util/log_utils.py
import logging
import os


def setup_logging2(log_type_name):
    log_directory = "/home/recording/"
    log_filename = log_type_name
    full_log_path = os.path.join(log_directory, log_filename)

    # Create log directory if it does not exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logging.basicConfig(
        filename=full_log_path,
        filemode="a",  # Change to 'a' to append to the log file
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )