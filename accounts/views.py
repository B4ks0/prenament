from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from functools import wraps

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect_by_role(user)
        error = 'Username atau password salah'
    return render(request, 'login.html', {'error': error})

def redirect_by_role(user):
    if user.role == 'ibu':
        return redirect('ibu:beranda')
    elif user.role == 'kader':
        return redirect('kader:beranda')
    elif user.role == 'petugas':
        return redirect('petugas:beranda')
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')
