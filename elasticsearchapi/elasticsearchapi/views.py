from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status

#create super user
@api_view(['GET'])
def create_superuser(request):
    User.objects.create_superuser('admin', 'admin@example.com', '12345678')

    return JsonResponse({'massege': 'ok'}, status=status.HTTP_200_OK)