from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Book
from .search import index_book, delete_book, create_index

# Ensure index exists when app starts
create_index()

@receiver(post_save, sender=Book)
def index_book_after_save(sender, instance, **kwargs):
    index_book(instance)

@receiver(post_delete, sender=Book)
def delete_book_after_delete(sender, instance, **kwargs):
    delete_book(instance.id)
