# -*- coding: utf-8 -*-

# Scraping.py

import urllib.request
import re
from urllib.error import URLError, HTTPError, ContentTooShortError

def download(url, num_retries=3, user_agent='wswp'):
    print('Downloading:', url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    try:
        html = urllib.request.urlopen(url).read()
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
            # recursively retry 5xx HTTP errors
                return download(url, num_retries - 1)
    return html

def crawl_sitemap(url):
    """ Crawl from the given start URL following links matched by
link_regex
    """
    sitemap = download(url)
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    for link in links:
        html = download(link)

    return None