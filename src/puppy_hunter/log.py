import logging
import logging.config
import os.path


def configure_logging(config_path):
    config = os.path.join(config_path, "logger.conf")
    print(config)
    logging.config.fileConfig(fname=config, disable_existing_loggers=False)


def get_logger():
    return logging.getLogger("puppyLogger")
