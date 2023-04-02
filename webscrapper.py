import requests
from bs4 import BeautifulSoup
from graphviz import Digraph
import hashlib

# function to create hash for URL to cluster nodes
def create_hash(url):
    hash_object = hashlib.sha256(url.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig[:10]

# function to get title and links recursively
def get_links(url, depth, dot, visited):
    # stop when reaching depth limit or already visited url
    if depth <= 0 or url in visited:
        return

    # get html content and parse with beautifulsoup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # get title and add node to dot graph
    title = soup.title.string.strip()
    node_id = create_hash(url)
    dot.node(node_id, title, href=url)

    # add url to visited set
    visited.add(url)

    # find all links in page
    for link in soup.find_all('a'):
        href = link.get('href')

        # skip if link is empty or just a fragment
        if not href or href.startswith('#'):
            continue

        # check if link is absolute or relative
        if href.startswith('http'):
            child_url = href
        else:
            # handle relative links
            child_url = url + '/' + href

        # get child title and add node to dot graph
        child_title = link.string.strip()
        child_id = create_hash(child_url)
        dot.node(child_id, child_title, href=child_url)

        # add edge between parent and child nodes
        dot.edge(node_id, child_id)

        # recursively visit child node
        get_links(child_url, depth-1, dot, visited)


# main function to run web scraper and generate dot file
def main(title_name, base_url):
    # create digraph object
    dot = Digraph(comment=title_name, format='svg')

    # set depth limit for recursion
    max_depth = 2

    # create visited set to avoid revisiting same url
    visited = set()

    # scrape base url
    get_links(base_url, max_depth, dot, visited)

    # generate dot file
    dot.render('output', view=True)


# example usage
main('Name', 'https://example.com')
