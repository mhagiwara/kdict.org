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
            'word_id': {
                'type': 'keyword'
            }
        }
    }
}


def format_entry(entry, prev_entry):
    """Receive an entry from the YAML file and format it for indexing."""
    result = dict(entry)    # shallow copy

    # Generate unique ID for retrieving
    if prev_entry and entry['word'] == prev_entry['word']:
        index = prev_entry.get('index', 1) + 1
        word_id = '{}-{}'.format(entry['word'], index)
        entry['index'] = index
    else:
        word_id = entry['word']
    result['word_id'] = word_id

    # Concat all defs for snippet
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
        prev_entry = None
        for entry in data:
            entry_formatted = format_entry(entry, prev_entry)
            prev_entry = entry

            es.index(index=KEDICT_INDEX, body=entry_formatted)
            print('Indexed: {} as {}'.format(entry_formatted['word'],
                                             entry_formatted['word_id']))


if __name__ == '__main__':
    main(sys.argv[1])
