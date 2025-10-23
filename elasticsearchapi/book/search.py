# search.py
import os
import time
import logging
from elasticsearch import Elasticsearch, exceptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ELASTIC_HOST = os.environ.get("ELASTICSEARCH_HOST", "http://esearch:9200")
INDEX_NAME = "books"

_es_client = None

def get_es_client():
    global _es_client
    if _es_client is None:
        # Create client lazily (so container/DNS can come up first)
        _es_client = Elasticsearch(
            [ELASTIC_HOST],
            # optional: you can set timeouts
            request_timeout=30,
        )
    return _es_client

def wait_for_es(timeout=120):
    """Wait until Elasticsearch is ready and reachable."""
    es = get_es_client()
    start_time = time.time()
    while True:
        try:
            # Use ping; it can return False or raise
            if es.ping():
                logger.info("Elasticsearch is ready!")
                return True
            else:
                logger.info("Elasticsearch ping returned False; retrying...")
        except exceptions.ConnectionError as e:
            logger.info(f"Elasticsearch connection error: {e}; retrying...")
        except Exception as e:
            logger.warning(f"Elasticsearch unexpected error: {e}; retrying...")

        if time.time() - start_time > timeout:
            raise Exception(f"Elasticsearch not available after {timeout}s")
        time.sleep(1)

def create_index():
    # ensure ES is ready first
    wait_for_es()
    es = get_es_client()
    try:
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(
                index=INDEX_NAME,
                body={
                    "mappings": {
                        "properties": {
                            "book_id": {"type": "text"},
                            "title": {"type": "text"},
                            "author": {"type": "text"},
                            "description": {"type": "text"},
                        }
                    }
                },
            )
            logger.info(f"Created index {INDEX_NAME}")
        else:
            logger.info(f"Index {INDEX_NAME} already exists")
    except Exception as e:
        logger.exception(f"Failed to create index {INDEX_NAME}: {e}")
        raise

def index_book(book):
    es = get_es_client()
    try:
        es.index(
            index=INDEX_NAME,
            id=book.book_id,
            body={
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
            },
        )
    except Exception as e:
        logger.exception(f"Failed to index book id={book.book_id}: {e}")

def delete_book(book_id):
    es = get_es_client()
    try:
        es.delete(index=INDEX_NAME, id=book_id, ignore=[404])
    except Exception as e:
        logger.exception(f"Failed to delete book id={book_id}: {e}")

# search.py

def elastic_search_books(query, from_=0, size=10):
    es = get_es_client()
    try:
        # Build the flexible search query
        response = es.search(
            index=INDEX_NAME,
            body={
                "query": {
                    "bool": {
                        "should": [
                            # Fuzzy match (handles typos and near matches)
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title", "author", "description"],
                                    "fuzziness": "AUTO",
                                    "boost": 3  # Give fuzzy match more importance
                                }
                            },
                            # Wildcard match (substring search)
                            {"wildcard": {"title": {"value": f"*{query.lower()}*", "boost": 2}}},
                            {"wildcard": {"author": {"value": f"*{query.lower()}*", "boost": 2}}},
                            {"wildcard": {"description": {"value": f"*{query.lower()}*", "boost": 1}}},
                            # Prefix match (start-of-word search)
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title", "author", "description"],
                                    "type": "phrase_prefix",
                                    "boost": 2
                                }
                            },
                        ]
                    }
                },
                "from": from_,
                "size": size
            }
        )

        # Extract and sort results by score (descending)
        # results = [
        #     {
        #         "_score": hit["_score"],
        #         "book_id": hit["_source"]["book_id"],
        #         "title": hit["_source"]["title"],
        #         "author": hit["_source"]["author"],
        #         "description": hit["_source"]["description"],
        #     }
        #     for hit in sorted(response["hits"]["hits"], key=lambda x: x["_score"], reverse=True)
        # ]

        # return results
        return response

    except Exception as e:
        logger.exception(f"Search failed for query='{query}': {e}")
        return []

def get_es_search(query, from_=0, size=10):
    response = elastic_search_books(query, from_=from_, size=size)
    results = [
            {
                "_score": hit["_score"],
                "book_id": hit["_source"]["book_id"],
                "title": hit["_source"]["title"],
                "author": hit["_source"]["author"],
                "description": hit["_source"]["description"],
            }
            for hit in sorted(response["hits"]["hits"], key=lambda x: x["_score"], reverse=True)
        ]
    return results

def get_book_ids(query, from_=0, size=10):
    response = elastic_search_books(query, from_=from_, size=size)
    book_ids = [int(hit["_source"]["book_id"]) for hit in response["hits"]["hits"]]
    return book_ids

# Previous simpler search implementation (commented out)
# def search_books(query, size=10):
#     es = get_es_client()
#     try:
#         response = es.search(
#             index=INDEX_NAME,
#             body={
#                 "query": {
#                     "bool": {
#                     "should": [
#                         {"prefix": {"title": query.lower()}},
#                         {"prefix": {"author": query.lower()}},
#                         {"prefix": {"description": query.lower()}},
#                     ]
#                 }
#                     #for full text search use this
#                     # "multi_match": {
#                     #     "query": query,
#                     #     "fields": ["title", "author", "description"],
#                     # }
#                 },
#                 "size": size,
#             },
#         )
#         return [hit["_source"] for hit in response["hits"]["hits"]]
#     except Exception as e:
#         logger.exception(f"Search failed for query='{query}': {e}")
#         return []
