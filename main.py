import os

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, send_from_directory, abort
import math

app = Flask(__name__)
es = Elasticsearch(['es'])

KEDICT_INDEX = 'kedict'
RESULTS_PER_PAGE = 20

@app.route('/health')
def health():
    return "alive"

@app.route('/')
def home():
    return render_template('index.html')

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

    # calculate pagination-related info
    total_hits = res['hits']['total']['value']
    num_pages = math.ceil(total_hits / RESULTS_PER_PAGE)
    pagination = []
    if current_page > 1:
        pagination.append({'page': 'previous',
                           'link': '/search?q={}&p={}'.format(query,
                                                              current_page - 1)})
    for p in range(max(1, current_page - 4), min(num_pages, current_page + 4)+1):
        pagination.append({'page': p,
                           'link': '/search?q={}&p={}'.format(query, p),
                           'active': p == current_page})
    if current_page < num_pages:
        pagination.append({'page': 'next',
                           'link': '/search?q={}&p={}'.format(query,
                                                              current_page + 1)})

    hits.extend(hit['_source'] for hit in res['hits']['hits'])
    print(pagination)

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
    hits = []
    body = {
        'query': {
            'match': {
                'tags': tag
            }
        },
        'size': RESULTS_PER_PAGE
    }
    res = es.search(index=KEDICT_INDEX, body=body)
    hits.extend(hit['_source'] for hit in res['hits']['hits'])
    print(res)

    return render_template('search.html', hits=hits)

@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('css', path)

if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
