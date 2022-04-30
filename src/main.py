# https://sf.ldgr.fr/api/
# https://sf.ldgr.fr/api/chapters/one-piece

import os
from typing import TYPE_CHECKING, Generator, Any
import re
from functools import partial

from mloader import loader
from mloader.exporter import RawExporter
import requests
import feedparser

INTERVAL = 60

if TYPE_CHECKING:
    from feedparser import FeedParserDict


def get_chapters(parsed_feed: "FeedParserDict") -> Generator[tuple[int, Any], None, None]:
    for entry in parsed_feed.entries:
        if result := re.search(r'\d+$', entry.link):
            chapter_number = int(result.group(0))
        else:
            continue

        yield chapter_number, entry


def main():
    parsed_feed: "FeedParserDict" = feedparser.parse('https://scantrad.net/rss/one-piece')

    print(f"Parsing {parsed_feed.feed.title} at {parsed_feed.feed.link}")

    print(parsed_feed.entries[0].keys())
    for chapter_number, entry in get_chapters(parsed_feed):
        destination = f"./one-piece/{chapter_number}"
        if os.path.isdir(destination): continue

        os.makedirs(destination)

        exporter = partial(RawExporter, destination=destination, add_chapter_title=False)
        manga_loader = loader.MangaLoader(exporter)

        print(f"{chapter_number} - {entry.title}")
    # Récupération du dernier feed
    # if len(news_feed.entries):
    #     print("Alert: {} \nLink: {}".format(news_feed.entries[0].title, news_feed.entries[0].link))


if __name__ == "__main__":
    main()
