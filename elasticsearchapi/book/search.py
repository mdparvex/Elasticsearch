from elasticsearch import Elasticsearch, exceptions
import time

es = Elasticsearch("http://elasticsearch:9200")

INDEX_NAME = "books"

def wait_for_es(timeout=60):
    """Wait until Elasticsearch is ready"""
    start_time = time.time()
    while True:
        try:
            if es.ping():
                print("Elasticsearch is ready!")
                break
        except exceptions.ConnectionError:
            pass
        if time.time() - start_time > timeout:
            raise Exception("Elasticsearch not available after 30s")
        time.sleep(1)

def create_index():
    wait_for_es()
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "author": {"type": "text"},
                        "description": {"type": "text"},
                    }
                }
            },
        )

def index_book(book):
    es.index(
        index=INDEX_NAME,
        id=book.id,
        body={
            "title": book.title,
            "author": book.author,
            "description": book.description,
        },
    )

def delete_book(book_id):
    es.delete(index=INDEX_NAME, id=book_id, ignore=[404])

def search_books(query):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "author", "description"],
                }
            }
        },
    )
    return [hit["_source"] for hit in response["hits"]["hits"]]
