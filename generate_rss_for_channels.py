#!/usr/bin/env python
# Read channels.txt and get RSS for each.
# Generate one single RSS for all channels combined.
# By Apie 2021-11-22
import requests
import feedparser
import dateparser
import feedgenerator
import datetime
import shelve
from sys import argv
from os import path
from lxml import html


SCRIPT_DIR = path.dirname(path.realpath(__file__))
DB_FILE = path.join(SCRIPT_DIR, 'rss_urls.db')
RSS_BASE_USER = 'https://www.youtube.com/feeds/videos.xml?user='
RSS_BASE_CHANNEL = 'https://www.youtube.com/feeds/videos.xml?channel_id='
NOW = datetime.datetime.now(datetime.timezone.utc)
TWO_WEEKS_AGO = NOW - datetime.timedelta(weeks=2)
TWO_YEARS_AGO = NOW - datetime.timedelta(weeks=100)
ONE_YEAR_AGO = NOW - datetime.timedelta(weeks=52)
CUTOFF = ONE_YEAR_AGO
session = requests.Session()

def _channel_url_to_rss_url(channel_url):
    # https://stackoverflow.com/questions/66934826/accept-cookies-consent-from-youtube
    response = session.get(channel_url, timeout=3, cookies={'CONSENT': 'YES+1'})
    response.raise_for_status()
    doc = html.fromstring(response.text)
    rss_url = doc.xpath('//link[@type="application/rss+xml"]/@href')[0]
    return rss_url

def channel_url_to_rss_url(url):
    with shelve.open(DB_FILE) as db:
        try:
            chan_id = db[url]
        except KeyError:
            db[url] = _channel_url_to_rss_url(url)
            chan_id = db[url]
    return chan_id

def yield_channel_entry(channel_url):
    if '/user/' in channel_url:
        username = channel_url.split('/user/')[1]
        rss_url = RSS_BASE_USER + username
    elif '/channel/' in channel_url:
        channel_id = channel_url.split('/channel/')[1]
        rss_url = RSS_BASE_CHANNEL + channel_id
    elif '/@' in channel_url:
        rss_url = channel_url_to_rss_url(channel_url)
    else:
        raise NotImplementedError('Unknown channel url type')
    feed = feedparser.parse(rss_url)
    for i, entry in enumerate(feed.entries):  # Sorted on publish date
        entry['published_datetime'] = dateparser.parse(entry['published'])
        if entry['published_datetime'] < CUTOFF:
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
