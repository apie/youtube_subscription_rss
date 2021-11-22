#!/usr/bin/env python
#Read channels.txt and get RSS for each.
#Generate one single RSS for all channels combined.
import requests
import feedparser
import dateparser
import feedgenerator


RSS_BASE_USER = 'https://www.youtube.com/feeds/videos.xml?user='
RSS_BASE_CHANNEL = 'https://www.youtube.com/feeds/videos.xml?channel_id='


def get_channel_feed(channel_url):
    if '/user/' in channel_url:
        username = channel_url.split('/user/')[1]
        rss_url = RSS_BASE_USER+username
    else:
        channel_id = channel_url.split('/channel/')[1]
        rss_url = RSS_BASE_CHANNEL+channel_id
    response = requests.get(channel_url)
    response.raise_for_status()
    feed = feedparser.parse(rss_url)
    print(rss_url)
    print(len(feed.entries))
    for entry in feed.entries:
        yield entry

def get_items(channels):
    for channel in channels:
        yield from get_channel_feed(channel)


if __name__ == '__main__':
    with open('channels.txt') as c:
        channels = c.readlines()
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
            pubdate=dateparser.parse(item['published']),
        )
    with open('complete.rss', 'w') as f:
        feed.write(f, encoding='utf-8')
