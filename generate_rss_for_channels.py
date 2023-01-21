#!/usr/bin/env python
# Read channels.txt and get RSS for each.
# Generate one single RSS for all channels combined.
# By Apie 2021-11-22
import requests
import feedparser
import dateparser
import feedgenerator
import datetime
from sys import argv
from os import path


RSS_BASE_USER = 'https://www.youtube.com/feeds/videos.xml?user='
RSS_BASE_CHANNEL = 'https://www.youtube.com/feeds/videos.xml?channel_id='
NOW = datetime.datetime.now(datetime.timezone.utc)
TWO_WEEKS_AGO = NOW - datetime.timedelta(weeks=2)
TWO_YEARS_AGO = NOW - datetime.timedelta(weeks=100)
session = requests.Session()


def yield_channel_entry(channel_url):
    if '/user/' in channel_url:
        username = channel_url.split('/user/')[1]
        rss_url = RSS_BASE_USER + username
    else:
        channel_id = channel_url.split('/channel/')[1]
        rss_url = RSS_BASE_CHANNEL + channel_id
    response = session.get(channel_url, timeout=3)
    response.raise_for_status()
    feed = feedparser.parse(rss_url)
    for i, entry in enumerate(feed.entries):  # Sorted on publish date
        entry['published_datetime'] = dateparser.parse(entry['published'])
        if entry['published_datetime'] < TWO_YEARS_AGO:
            if i == 0:
                print(f"Skipped {channel_url!r}")
                return  # Skip whole channel since first (newest) item is too old.
            else:
                continue  # Skip just this entry
        yield entry


def get_items(channels):
    for channel in channels:
        yield from yield_channel_entry(channel.strip())


def write_complete_rss_for_channels(channels, filename):
    feed = feedgenerator.Rss201rev2Feed(
        title="Youtube subscriptions complete RSS",
        description="Youtube subscriptions complete RSS",
        link="https://www.youtube.com/feed/channels",
    )
    for item in get_items(channels):
        feed.add_item(
            title=item['title'],
            link=item['link'],
            description=item['title'],
            pubdate=item['published_datetime'],
            author_name=item['author'],
        )
    with open(path.join(path.dirname(path.realpath(argv[0])), filename), 'w') as f:
        feed.write(f, encoding='utf-8')


if __name__ == '__main__':
    with open(path.join(path.dirname(path.realpath(argv[0])), 'channels.txt')) as c:
        channels = c.readlines()
    write_complete_rss_for_channels(channels, 'youtube_subscriptions_complete.rss')
