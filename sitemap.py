import requests
import re
from urllib.parse import urldefrag, urlparse, urlunparse


def get_root(url):
    """Returns URL of the root of the site a given page belongs to"""
    struct_url = urlparse(url)
    struct_url_root = (struct_url[0], struct_url[1], '', '', '', '')
    return urlunparse(struct_url_root)


def get_title(text):
    """Returns the title of a given html document"""
    pattern = r'(?<=<title>).*(?=</title>)'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return ''


def get_links(text, root, page_url):
    """Given an html document, return all URLs pointing to resources
    within the same domain

    Args:
        text (str): content of the html document
        root (str): URL of the root
        page_url (str): URL of the html document
    Returns:
        set of URLs
    """
    # TODO Add pattern for relative paths without leading forward slash

    # Build list of URLs from links with absolute path
    # Remove fragment identifiers from URLs
    pattern_abs = r'<a.*?href="({})(/.*?)?".*?>.*?</a>'.format(root)
    links_abs = [urldefrag(''.join(match))[0] for match in re.findall(pattern_abs, text)]

    # Build list of URLs from links with relative path
    # Remove fragment identifiers from URLs
    pattern_rel = r'<a.*?href="(/.*?)".*?>.*?</a>'.format(root)
    links_rel = [urldefrag(root + link)[0] for link in re.findall(pattern_rel, text)]

    # Build list of all URLs excluding URLs of itself
    links = [link for link in links_abs + links_rel if link != page_url]
    return set(links)


def get_page_text(url):
    """Get content of a web page

    Args:
        url (str): URL of the web page

    Returns:
        tuple with the following elements:
            content of the web page (str) or None if an error occurred
            information on request (str)
    """
    try:
        # Send request
        r = requests.get(url)

        # Raise HTTPError if request was unsuccessful
        r.raise_for_status()

        # Verify that the url was pointing to an html document
        c_type = r.headers.get('content-type', '') if r.headers else {}
        assert 'text/html' in c_type
    except (requests.HTTPError, requests.ConnectionError) as e:
        return None, 'Unsuccessful request to {}: {}'.format(url, e)
    except AssertionError:
        return None, 'Resource at {} is not an html document'.format(url)
    else:
        return r.text, 'OK'


def site_map(url):
    """Create a map of a website given URL of a page from this site

    Args:
        url (str): URL of a web page

    Returns:
        site map in form of a dictionary with the key:value pairs in the following format:
            url: {
                'title': title of the page (str)
                'links': set of all target URLs with the domain on the page
                    without anchor links
            }
    """
    site_map_dict = {}  # container for the map of the website
    root_url = get_root(url)  # url of the root of the website
    to_visit = [root_url]  # container for web pages to be visited by the crawler
    visited = []  # container for web pages already visited by the crawler
    request_count = 0
    while to_visit:
        #  Print info on the number of requests
        request_count += 1
        if request_count % 10 == 0:
            print('Sending request #{}'.format(request_count))

        # Get content of a web page from to_visit
        page_url = to_visit.pop(0)
        text, msg = get_page_text(page_url)

        # If request was unsuccessful proceed to a next web page
        if msg != 'OK':
            print(msg)
            continue

        # Add the web page to the site map dictionary
        title = get_title(text)
        links = get_links(text, root_url, page_url)
        site_map_dict[page_url] = {'title': title, 'links': links}

        # Housekeeping
        visited.append(page_url)
        to_visit += [link for link in links if link not in visited]
    return site_map_dict
