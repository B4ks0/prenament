from .views import get_unread_count


def notifikasi_unread(request):
    return {'notifikasi_unread': get_unread_count(request.user)}
