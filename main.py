import os

from elasticsearch import Elasticsearch
from flask import Flask, render_template

app = Flask(__name__)
es = Elasticsearch(['es'])

KEDICT_INDEX = 'kedict'

@app.route('/health')
def health():
    return "alive"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search/<query>')
def search(query):
    hits = []
    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'word': query}}})
    hits.extend(res['hits']['hits'])

    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'defs_all': query}}})
    hits.extend(res['hits']['hits'])

    res = es.search(index=KEDICT_INDEX, body={'query': {'match': {'romaja': query}}})
    hits.extend(res['hits']['hits'])

    return render_template('search.html', hits=hits)

if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
