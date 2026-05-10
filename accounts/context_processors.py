def user_foto(request):
    if request.user.is_authenticated:
        return {'user_foto_url': request.user.get_foto_url()}
    return {'user_foto_url': None}
