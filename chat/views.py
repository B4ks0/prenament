from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from accounts.views import role_required
from accounts.models import CustomUser
from ibu.models import IbuProfil
from kader.models import KaderProfil
from .models import Pesan


# ── Kader: list ibu untuk chat ──────────────────────────────────────────
@role_required('kader')
def kader_list(request):
    try:
        kader = request.user.kader_profil
    except KaderProfil.DoesNotExist:
        return redirect('kader:beranda')

    ibu_list = IbuProfil.objects.filter(kader=kader).select_related('user')
    # Hitung pesan belum dibaca per ibu
    conv_data = []
    for profil in ibu_list:
        unread = Pesan.objects.filter(pengirim=profil.user, penerima=request.user, dibaca=False).count()
        last = Pesan.get_conversation(request.user, profil.user).last()
        conv_data.append({'profil': profil, 'unread': unread, 'last': last})
    # Sort: ada pesan terbaru dulu
    conv_data.sort(key=lambda x: x['last'].created_at if x['last'] else timezone.datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    return render(request, 'chat/kader_list.html', {'conv_data': conv_data})


# ── Room: kader ↔ ibu ───────────────────────────────────────────────────
@role_required('kader')
def kader_room(request, ibu_pk):
    try:
        kader = request.user.kader_profil
    except KaderProfil.DoesNotExist:
        return redirect('kader:beranda')

    ibu_profil = get_object_or_404(IbuProfil, pk=ibu_pk, kader=kader)
    partner = ibu_profil.user

    if request.method == 'POST':
        isi = request.POST.get('isi', '').strip()
        if isi:
            Pesan.objects.create(pengirim=request.user, penerima=partner, isi=isi)
        return redirect('chat:kader_room', ibu_pk=ibu_pk)

    # Tandai semua pesan dari ibu sebagai dibaca
    Pesan.objects.filter(pengirim=partner, penerima=request.user, dibaca=False).update(dibaca=True)
    msgs = list(Pesan.get_conversation(request.user, partner))
    last_id = msgs[-1].pk if msgs else 0
    return render(request, 'chat/room.html', {
        'partner': partner,
        'partner_profil': ibu_profil,
        'messages': msgs,
        'last_id': last_id,
        'back_url': 'kader:chat_list',
        'send_url': request.path,
        'poll_url': f'/chat/poll/{partner.pk}/',
        'me': request.user,
    })


# ── Room: ibu ↔ kader ───────────────────────────────────────────────────
@role_required('ibu')
def ibu_room(request):
    try:
        ibu_profil = request.user.ibu_profil
    except IbuProfil.DoesNotExist:
        return redirect('ibu:beranda')

    if not ibu_profil.kader:
        return render(request, 'chat/room.html', {
            'no_kader': True, 'me': request.user,
        })

    partner = ibu_profil.kader.user

    if request.method == 'POST':
        isi = request.POST.get('isi', '').strip()
        if isi:
            Pesan.objects.create(pengirim=request.user, penerima=partner, isi=isi)
        return redirect('chat:ibu_room')

    Pesan.objects.filter(pengirim=partner, penerima=request.user, dibaca=False).update(dibaca=True)
    msgs = list(Pesan.get_conversation(request.user, partner))
    last_id = msgs[-1].pk if msgs else 0
    return render(request, 'chat/room.html', {
        'partner': partner,
        'partner_profil': ibu_profil.kader,
        'messages': msgs,
        'last_id': last_id,
        'back_url': 'ibu:beranda',
        'send_url': request.path,
        'poll_url': f'/chat/poll/{partner.pk}/',
        'me': request.user,
    })


# ── AJAX: poll pesan baru ────────────────────────────────────────────────
def poll_messages(request, partner_pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth'}, status=401)
    partner = get_object_or_404(CustomUser, pk=partner_pk)
    since_id = int(request.GET.get('since', 0))

    from django.db.models import Q
    qs = Pesan.objects.filter(
        Q(pengirim=request.user, penerima=partner) |
        Q(pengirim=partner, penerima=request.user)
    ).filter(pk__gt=since_id).order_by('created_at')

    # Tandai masuk sebagai dibaca
    qs.filter(penerima=request.user, dibaca=False).update(dibaca=True)

    data = [{
        'id': m.pk,
        'isi': m.isi,
        'mine': m.pengirim_id == request.user.pk,
        'time': m.created_at.strftime('%H:%M'),
    } for m in qs]

    return JsonResponse({'messages': data})
