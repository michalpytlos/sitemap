# sitemap
This program is meant to serve as a simple tool for creation of website maps. Given URL of an html document, sitemap creates a map of the domain the document is on in form of a Python dictionary.

## Prerequisites
* Python 3.7 (available from [python.org](https://www.python.org/downloads/))
* Requests with its dependencies. Install using the provided requirements.txt file: `pip install -r requirements.txt`

## Usage
The program is meant to be used via the **site_map()** function defined in the **sitemap** module.

Usage from the Python interpreter:
1. Navigate to the directory containing **sitemap.py** and run `python` (for virtualenv with python3.7)
2. Import the function: `from sitemap import site_map`
3. Create a map: `site_map(site_url)`

**site_map()** returns a dictionary with the key:value pairs in the following format:
```
page_url: {
    'title': title of the page (str)
    'links': set of all target URLs within the domain on the page
}
```

## How it works
1. Extract URL of the root of the website from the input url
2. Get the content of the resource at the root using the requests package
3. From the content using regex, extract page title and all the links to other pages on the same domain
4. Add URLs extracted in step 3 which have not been visited yet to a list of URLs to visit
5. Repeat steps 2-4 for all URLs in the to visit list until the list is empty
