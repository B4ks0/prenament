from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from accounts.views import role_required
from ibu.models import IbuProfil, SkriningHasil
from kader.models import KaderProfil
from .models import Notifikasi


def _auto_reminder(user):
    """Buat reminder skrining jika ibu belum skrining >30 hari dan belum ada reminder aktif."""
    try:
        profil = user.ibu_profil
    except IbuProfil.DoesNotExist:
        return
    batas = timezone.now() - timedelta(days=30)
    sudah_skrining_baru = SkriningHasil.objects.filter(ibu=profil, created_at__gte=batas).exists()
    if sudah_skrining_baru:
        return
    sudah_ada_reminder = Notifikasi.objects.filter(
        penerima=user, tipe='reminder', dibaca=False,
        created_at__gte=batas,
    ).exists()
    if not sudah_ada_reminder:
        Notifikasi.objects.create(
            penerima=user,
            pengirim=None,
            judul='Waktunya Skrining Kesehatan Mental',
            pesan=(
                'Sudah lebih dari 30 hari sejak skrining terakhir Anda. '
                'Lakukan skrining PRAQ-R2 sekarang untuk memantau kesehatan mental Anda dan si kecil.'
            ),
            tipe='reminder',
        )


# ── Ibu: list notifikasi ────────────────────────────────────────────────
@role_required('ibu')
def ibu_list(request):
    _auto_reminder(request.user)
    notifs = Notifikasi.objects.filter(penerima=request.user)
    # Tandai semua sebagai dibaca saat halaman dibuka
    notifs.filter(dibaca=False).update(dibaca=True)
    return render(request, 'notifikasi/ibu_list.html', {'notifs': notifs})


# ── Kader: kirim notifikasi ─────────────────────────────────────────────
@role_required('kader')
def kader_kirim(request):
    try:
        kader = request.user.kader_profil
    except KaderProfil.DoesNotExist:
        return redirect('kader:beranda')

    ibu_list = IbuProfil.objects.filter(kader=kader).select_related('user')

    if request.method == 'POST':
        judul  = request.POST.get('judul', '').strip()
        pesan  = request.POST.get('pesan', '').strip()
        tipe   = request.POST.get('tipe', 'pesan')
        target = request.POST.get('target', 'semua')

        if judul and pesan:
            if target == 'semua':
                penerima_list = [p.user for p in ibu_list]
            else:
                try:
                    ibu_profil = IbuProfil.objects.get(pk=int(target), kader=kader)
                    penerima_list = [ibu_profil.user]
                except (IbuProfil.DoesNotExist, ValueError):
                    penerima_list = []

            for penerima in penerima_list:
                Notifikasi.objects.create(
                    penerima=penerima,
                    pengirim=request.user,
                    judul=judul,
                    pesan=pesan,
                    tipe=tipe,
                )
            messages.success(request, f'Notifikasi terkirim ke {len(penerima_list)} ibu.')
            return redirect('notifikasi:kader_kirim')
        else:
            messages.error(request, 'Judul dan pesan wajib diisi.')

    riwayat = Notifikasi.objects.filter(pengirim=request.user).order_by('-created_at')[:20]
    return render(request, 'notifikasi/kader_kirim.html', {
        'ibu_list': ibu_list,
        'riwayat': riwayat,
        'tipe_choices': Notifikasi.TIPE_CHOICES,
    })


# ── Shared: jumlah notifikasi belum dibaca (dipanggil context processor) ─
def get_unread_count(user):
    if not user.is_authenticated or user.role != 'ibu':
        return 0
    _auto_reminder(user)
    return Notifikasi.objects.filter(penerima=user, dibaca=False).count()
