import os

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, send_from_directory, abort

app = Flask(__name__)
es = Elasticsearch(['es'])

KEDICT_INDEX = 'kedict'
RESULTS_PER_PAGE = 30

@app.route('/health')
def health():
    return "alive"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    hits = []
    body = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['word^2', 'defs_all^2', 'romaja'],
            }
        },
        'size': RESULTS_PER_PAGE
    }
    res = es.search(index=KEDICT_INDEX, body=body)
    hits.extend(hit['_source'] for hit in res['hits']['hits'])
    print(res)

    return render_template('search.html', hits=hits, query=query)

@app.route('/word/<word_id>')
def word(word_id):
    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'word_id': word_id}}})
    num_hits = res['hits']['total']['value']
    if num_hits == 0:
        abort(404)

    entry = res['hits']['hits'][0]['_source']
    return render_template('word.html', entry=entry)

@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('css', path)

if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
