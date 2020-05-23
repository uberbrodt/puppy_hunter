# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
import click
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


@click.command()
def run():
    process = CrawlerProcess(settings={"FEEDS": {"puppies.json": {"format": "json"}}})
    process.crawl(PuppyCrawler)
    process.start()
