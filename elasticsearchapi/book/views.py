from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Book
from .serializers import BookSerializer
from .search import get_es_search, get_book_ids
from rest_framework import status

@api_view(["POST"])
def add_book(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        book = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

@api_view(["GET"])
def search(request):
    query = request.query_params.get("q", "")
    from_ = int(request.query_params.get("from", 0))
    size = int(request.query_params.get("size", 10))
    results = get_es_search(query, from_=from_, size=size)
    return Response(results, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_book_details(request):
    query = request.query_params.get("q", "")
    from_ = int(request.query_params.get("from", 0))
    size = int(request.query_params.get("size", 10))
    book_ids = get_book_ids(query, from_=from_, size=size)
    books = Book.objects.filter(book_id__in=book_ids)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
