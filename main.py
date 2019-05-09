import os

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)
es = Elasticsearch(['es'])

KEDICT_INDEX = 'kedict'

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
    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'word': query}}})
    hits.extend(hit['_source'] for hit in res['hits']['hits'])

    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'defs_all': query}}})
    hits.extend(hit['_source'] for hit in res['hits']['hits'])

    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'romaja': query}}})
    hits.extend(hit['_source'] for hit in res['hits']['hits'])

    return render_template('search.html', hits=hits, query=query)

@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('css', path)

if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
