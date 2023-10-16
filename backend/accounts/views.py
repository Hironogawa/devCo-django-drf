from django.http import HttpResponse
from .models import User


def UserAccountView(request):
    username = request.user.username

    user = User.objects.get(username=username)
    return HttpResponse(f"Hello, {user.email}")
