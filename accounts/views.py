from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
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
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 hari
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


def profil_url_by_role(user):
    if user.role == 'ibu':
        return redirect('ibu:profil')
    elif user.role == 'kader':
        return redirect('kader:profil')
    elif user.role == 'petugas':
        return redirect('petugas:profil')
    return redirect('login')


def ganti_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    errors = {}
    success = False

    if request.method == 'POST':
        lama     = request.POST.get('password_lama', '')
        baru     = request.POST.get('password_baru', '')
        konfirm  = request.POST.get('konfirmasi', '')

        if not request.user.check_password(lama):
            errors['lama'] = 'Password lama tidak benar.'
        if len(baru) < 8:
            errors['baru'] = 'Password baru minimal 8 karakter.'
        if baru and konfirm and baru != konfirm:
            errors['konfirm'] = 'Konfirmasi password tidak cocok.'

        if not errors:
            request.user.set_password(baru)
            request.user.save()
            update_session_auth_hash(request, request.user)  # jaga sesi tetap aktif
            success = True

    return render(request, 'ganti_password.html', {'errors': errors, 'success': success})
