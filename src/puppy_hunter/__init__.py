# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
import click
import time
import puppy_hunter.db
import puppy_hunter.notify
from puppy_hunter.crawl import PuppyCrawler
from scrapy.crawler import CrawlerProcess

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


@click.group()
def cli():
    pass


@click.command()
@click.option("--dbpath", default=DEFAULT_DB_PATH, show_default=True)
@click.option("--tempdir", default=DEFAULT_TEMP_DIR, show_default=True)
def run(dbpath, tempdir):
    ut = int(time.time())
    puppy_file = f"{tempdir}/puppies_{ut}.json"
    process = CrawlerProcess(settings={"FEEDS": {puppy_file: {"format": "json"}}})
    process.crawl(PuppyCrawler)
    process.start()

    puppy_hunter.db.update_batch(dbpath, puppy_file)
    puppy_hunter.notify.updated_puppies_since(ut, dbpath)


@click.command()
@click.option("--dbpath", default=DEFAULT_DB_PATH, show_default=True)
def initialize(dbpath):
    puppy_hunter.db.initialize_db(dbpath)


cli.add_command(run)
cli.add_command(initialize)
