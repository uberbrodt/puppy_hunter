# -*- coding: utf-8 -*-
import os.path
import time
import logging

import click
from pkg_resources import DistributionNotFound, get_distribution
from scrapy.crawler import CrawlerProcess

import puppy_hunter.db
import puppy_hunter.log as log
import puppy_hunter.notify
from puppy_hunter.crawl import PuppyCrawler

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

DEFAULT_DB_PATH = "files/puppy_db.sqlite"
DEFAULT_TEMP_DIR = "files"
DEFAULT_LOG_PATH = "logs"
DEFAULT_CONFIG_PATH = "config"


@click.group()
def cli():
    pass


@click.command()
@click.option("--dbpath", default=DEFAULT_DB_PATH, show_default=True)
@click.option("--tempdir", default=DEFAULT_TEMP_DIR, show_default=True)
@click.option("--batch_time", default=None, show_default=True)
@click.option("--log_path", default=DEFAULT_LOG_PATH, show_default=True)
@click.option("--config_path", default=DEFAULT_CONFIG_PATH, show_default=True)
def run(dbpath, tempdir, batch_time, log_path, config_path):
    log.configure_logging(config_path)
    logger = log.get_logger()
    logger.info("Starting PuppyHunter run")
    if batch_time is None:
        ut = int(time.time())
    else:
        ut = int(batch_time)

    logger.info(f"batch_time is {ut}")

    puppy_file = f"{tempdir}/puppies_{ut}.json"

    if batch_time is None:
        process = CrawlerProcess(
            settings={
                "LOG_FILE": os.path.join(log_path, "scrapy.log"),
                "LOG_LEVEL": logging.INFO,
                "LOG_ENABLED": False,
                "FEEDS": {puppy_file: {"format": "json"}},
            }
        )
        process.crawl(PuppyCrawler)
        process.start()

    puppy_hunter.db.update_batch(dbpath, puppy_file)
    puppy_hunter.notify.send_updated_notifications(dbpath)


@click.command()
@click.option("--dbpath", default=DEFAULT_DB_PATH, show_default=True)
def initialize(dbpath):
    puppy_hunter.db.initialize_db(dbpath)


cli.add_command(run)
cli.add_command(initialize)
