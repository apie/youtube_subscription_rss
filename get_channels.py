#!/usr/bin/env python
# Gets user or channel link from your subscription page
#By Apie 2021-11-22

# URL = 'https://www.youtube.com/feed/channels'
#TODO automatic retrieve, for now use a downloaded HTML file.
from lxml import html

def get_channels():
    with open('Channel list - YouTube.html') as html_file:
        page = html.fromstring(html_file.read())
    return page.xpath("//a[@id='main-link']/@href")

if __name__ == '__main__':
    for c in get_channels():
        print(c)