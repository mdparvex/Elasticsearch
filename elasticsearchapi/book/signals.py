# signals.py
from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from .models import Book
from .search import index_book, delete_book, create_index
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_index_after_migrate(sender, **kwargs):
    """Create Elasticsearch index after migrations are done."""
    try:
        create_index()
    except Exception as e:
        logger.warning(f"[WARNING] Could not create Elasticsearch index: {e}")

@receiver(post_save, sender=Book)
def index_book_after_save(sender, instance, **kwargs):
    index_book(instance)

@receiver(post_delete, sender=Book)
def delete_book_after_delete(sender, instance, **kwargs):
    delete_book(instance.book_id)
