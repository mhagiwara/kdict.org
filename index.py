from elasticsearch import Elasticsearch

def main():
    es = Elasticsearch()

    settings = {
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
                }
            }
        }
    }

    # es.indices.delete(index='test-index')
    # es.indices.create(index='test-index', body=settings)

    doc = {
        'word': '가격',
        'romaja': 'gagyeok',
        'pos': 'n',
        'defs' : [
            {'def': 'monetary price'}
        ]
    }
    # res = es.index(index='test-index', body=doc)
    # print(res['result'])

    # res = es.indices.analyze(index='test-index', body={'field': 'word', 'text': '가격'})
    # print(res)

    res = es.search(index="test-index", body={"query": {"match": {"defs": "monetary"}}})
    print("Got %d Hits:" % res['hits']['total']['value'])
    print(res)


if __name__ == '__main__':
    main()
