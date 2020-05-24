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


@click.group()
def cli():
    pass


@click.command()
def run():
    ut = int(time.time())
    puppy_file = f"files/puppies_{ut}.json"
    puppy_db = "files/puppy_db.sqlite"
    process = CrawlerProcess(settings={"FEEDS": {puppy_file: {"format": "json"}}})
    process.crawl(PuppyCrawler)
    process.start()

    puppy_hunter.db.update_batch(puppy_db, puppy_file)
    puppy_hunter.notify.updated_puppies_since(ut, puppy_db)


@click.command()
def initialize():
    puppy_db = "files/puppy_db.sqlite"
    puppy_hunter.db.initialize_db(puppy_db)


cli.add_command(run)
cli.add_command(initialize)
