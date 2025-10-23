# Django + Elasticsearch + PostgreSQL

A fully dockerized Django application integrated with **Elasticsearch** for full-text search and **PostgreSQL** as the main database.  
It allows you to create, index, and search books in real-time through REST API endpoints.

---

## Features

-  **Full-text search** powered by Elasticsearch
-  **PostgreSQL** as the primary database
-  **Docker Compose** setup for easy deployment
-  **Signals-based auto indexing** (creates index on migrate & updates on save/delete)
-  **Partial search** support (via Wildcard / N-gram configuration)
-  Modular architecture (clean `search.py`, `signals.py`, `views.py` separation)

---

##  Project Structure

```
├── elasticsearchapi/
│   ├── book/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── search.py
│   │   ├── signals.py
│   │   └── serializers.py
│   ├── elasticsearchapi/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── Dockerfile
│   └── manage.py
│   ├── entrypoint.sh
│   └── supervisord.conf
├── docker-compose.yaml
├── .env
└── README.md
```

---

##  Requirements

- Docker 
- Docker Compose
- Python 3.12+ (if running locally without Docker)

---

##  Environment Variables (`.env`)

Create a `.env` file in the project root with the following values:

```bash
POSTGRES_DB=books_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

ELASTICSEARCH_HOST=http://esearch:9200

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin123
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

---

##  Run the Project (with Docker Compose)

1. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

2. **Access the services**
   - Django API → [http://localhost:8000](http://localhost:8000)
   - Elasticsearch → [http://localhost:9200](http://localhost:9200)
   - PostgreSQL → localhost:5433

3. **Verify Elasticsearch health**
   ```bash
   curl http://localhost:9200/
   ```

---

##  API Endpoints

###  Create a Book
**POST** `/books/add/`

**Request body:**
```json
{
  "title": "Beautiful Mind",
  "author": "John Nash",
  "description": "A story of a mathematical genius."
}
```

**Response:**
```json
{
  "book_id": 1,
  "title": "Beautiful Mind",
  "author": "John Nash",
  "description": "A story of a mathematical genius."
}
```

---

###  Search Books
**GET** `/books/search/?q=<query>`

**Example:**
```
GET http://127.0.0.1:8000/books/search/?q=beaut
```

**Response:**
```json
[
  {
    "book_id": 1,
    "title": "Beautiful Mind",
    "author": "John Nash",
    "description": "A story of a mathematical genius."
  }
]
```

 Supports **partial match** using wildcard search.

---

##  How Elasticsearch Integration Works

- On each **Django migration**, a signal (`post_migrate`) triggers creation of the index.
- On each **Book save/delete**, data is automatically **indexed or removed** from Elasticsearch.
- Search queries use `multi_match` + `wildcard` for flexible text searching across fields:
  - `title`
  - `author`
  - `description`

---

##  Docker Services Overview

| Service | Description | Port |
|----------|--------------|------|
| `django_app` | Django REST API backend | 8000 |
| `postgres_db` | PostgreSQL database | 5433 |
| `elasticsearch` | Elasticsearch search engine | 9200 |
| *(optional)* `kibana` | Web UI for Elasticsearch | 5601 |

---