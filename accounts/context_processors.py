def user_foto(request):
    if request.user.is_authenticated:
        return {'user_foto_url': request.user.get_foto_url()}
    return {'user_foto_url': None}


def chat_unread(request):
    if request.user.is_authenticated:
        from chat.models import Pesan
        count = Pesan.unread_count(request.user)
        return {'chat_unread': count}
    return {'chat_unread': 0}
