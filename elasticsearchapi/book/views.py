from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Book
from .serializers import BookSerializer
from .search import search_books
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
    results = search_books(query)
    return Response(results, status=status.HTTP_200_OK)
