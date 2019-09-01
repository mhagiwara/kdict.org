import os

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, send_from_directory, abort, redirect
from urllib.parse import urlparse, urlunparse
import math

app = Flask(__name__)
es = Elasticsearch(['es'])

KEDICT_INDEX = 'kedict'
RESULTS_PER_PAGE = 20


@app.before_request
def redirect_nonwww():
    """Redirect non-www requests to www."""
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'kdict.org':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'www.kdict.org'
        return redirect(urlunparse(urlparts_list), code=301)

@app.route('/health')
def health():
    return "alive"

@app.route('/')
def home():
    return render_template('index.html')

def _get_pagination(total_hits, current_page, page_to_link):
    """Calculate pagination-related info"""
    num_pages = math.ceil(total_hits / RESULTS_PER_PAGE)
    pagination = []
    pagination.append({'page': 'previous',
                       'link': page_to_link(current_page - 1),
                       'disabled': current_page == 1})
    for p in range(max(1, current_page - 4), min(num_pages, current_page + 4)+1):
        pagination.append({'page': p,
                           'link': page_to_link(p),
                           'active': p == current_page})
    pagination.append({'page': 'next',
                       'link': page_to_link(current_page + 1),
                       'disabled': current_page == num_pages})

    return pagination

@app.route('/search')
def search():
    query = request.args.get('q')
    current_page = int(request.args.get('p') or '1')     # 1-base

    hits = []
    body = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['word^2', 'defs_all^2', 'romaja'],
            }
        },
        'from': (current_page - 1) * RESULTS_PER_PAGE,
        'size': RESULTS_PER_PAGE
    }
    res = es.search(index=KEDICT_INDEX, body=body)
    hits.extend(hit['_source'] for hit in res['hits']['hits'])

    # calculate pagination-related info
    total_hits = res['hits']['total']['value']
    def _page_to_link(p):
        return '/search?q={}&p={}'.format(query, p)
    pagination = _get_pagination(total_hits, current_page, _page_to_link)

    return render_template('search.html',
                           hits=hits,
                           query=query,
                           pagination=pagination)

@app.route('/word/<word_id>')
def word(word_id):
    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'word_id': word_id}}})
    num_hits = res['hits']['total']['value']
    if num_hits == 0:
        abort(404)

    entry = res['hits']['hits'][0]['_source']
    return render_template('word.html', entry=entry)

@app.route('/tag/<tag>')
def tag(tag):
    title = {'topik1': 'TOPIK 1 Vocabulary List'}[tag]
    current_page = int(request.args.get('p') or '1')  # 1-base

    hits = []
    body = {
        'query': {
            'match': {
                'tags': tag
            }
        },
        'from': (current_page - 1) * RESULTS_PER_PAGE,
        'size': RESULTS_PER_PAGE
    }
    res = es.search(index=KEDICT_INDEX, body=body)
    hits.extend(hit['_source'] for hit in res['hits']['hits'])
    # calculate pagination-related info
    total_hits = res['hits']['total']['value']
    def _page_to_link(p):
        return '/tag/{}?p={}'.format(tag, p)
    pagination = _get_pagination(total_hits, current_page, _page_to_link)

    return render_template('search.html',
                           title=title,
                           hits=hits,
                           pagination=pagination)

@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('css', path)

if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
