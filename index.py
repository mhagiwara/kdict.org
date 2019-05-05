"""Given a CC-KEDICT file (kedict.yml), index it to ElasticSearch."""

import sys

import yaml
from elasticsearch import Elasticsearch

from main import KEDICT_INDEX

ES_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'ko_analyzer': {
                    'tokenizer': 'ko_tokenizer'
                }
            },
            'tokenizer': {
                'ko_tokenizer': {
                    'type': 'ngram',
                    'min_gram': 1,
                    'max_gram': 2,
                    'token_chars': [
                        'letter',
                        'digit'
                    ]
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'word': {
                'type': 'text',
                'analyzer': 'ko_analyzer',
            },
            'romaja': {
                'type': 'text',
                'analyzer': 'ko_analyzer'
            },
        }
    }
}


def format_entry(entry):
    result = dict(entry)

    defs_all = []
    defs = entry.get('defs', []) or []
    for definition in defs:
        defs_all.append(definition['def'])
    
    result['defs_all'] = ' '.join(defs_all)

    return result


def main(kedict_path):
    es = Elasticsearch()
    if es.indices.exists(index=KEDICT_INDEX):
        es.indices.delete(index=KEDICT_INDEX)

    es.indices.create(index=KEDICT_INDEX, body=ES_SETTINGS)

    with open(kedict_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        for entry in data:
            entry = format_entry(entry)
            es.index(index=KEDICT_INDEX, body=entry)
            print('Indexed: {}'.format(entry['word']))


if __name__ == '__main__':
    main(sys.argv[1])
