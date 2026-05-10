from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.views import role_required
from accounts.models import CustomUser
from ibu.models import IbuProfil, SkriningHasil
from .models import KaderProfil, Jadwal

def _get_kader(user):
    try:
        return user.kader_profil
    except KaderProfil.DoesNotExist:
        return KaderProfil.objects.create(user=user, posyandu='', wilayah='')

@role_required('kader')
def beranda(request):
    kader = _get_kader(request.user)
    ibu_list = IbuProfil.objects.filter(kader=kader)
    total_ibu = ibu_list.count()
    risiko_tinggi_list = [p for p in ibu_list if p.get_kategori_risiko() == 'Risiko Tinggi']
    jadwal_terdekat = Jadwal.objects.filter(kader=kader).order_by('tanggal').first()
    return render(request, 'kader/beranda.html', {
        'kader': kader,
        'total_ibu': total_ibu,
        'jumlah_risiko_tinggi': len(risiko_tinggi_list),
        'perhatian_khusus': risiko_tinggi_list,
        'jadwal_terdekat': jadwal_terdekat,
    })

@role_required('kader')
def daftar_ibu(request):
    kader = _get_kader(request.user)
    ibu_list = IbuProfil.objects.filter(kader=kader).select_related('user')
    return render(request, 'kader/daftar_ibu.html', {'ibu_list': ibu_list, 'kader': kader})

@role_required('kader')
def monitor(request):
    kader = _get_kader(request.user)
    ibu_list = list(IbuProfil.objects.filter(kader=kader).select_related('user'))

    tinggi = [p for p in ibu_list if p.get_kategori_risiko() == 'Risiko Tinggi']
    sedang = [p for p in ibu_list if p.get_kategori_risiko() == 'Risiko Sedang']
    rendah = [p for p in ibu_list if p.get_kategori_risiko() == 'Risiko Rendah']

    # Sort by score descending
    def get_score(p):
        return p.get_skor_terakhir()

    sorted_list = sorted(ibu_list, key=get_score, reverse=True)

    # Build monitor data
    monitor_data = []
    for p in sorted_list:
        skor = p.get_skor_terakhir()
        kategori = p.get_kategori_risiko()
        history = list(SkriningHasil.objects.filter(ibu=p).order_by('created_at')[:5].values_list('skor', flat=True))
        trend = 'flat'
        if len(history) >= 2:
            if history[-1] > history[-2]:
                trend = 'up'
            elif history[-1] < history[-2]:
                trend = 'down'
        pct = int((skor / 55) * 100)
        monitor_data.append({
            'profil': p,
            'skor': skor,
            'kategori': kategori,
            'history': history,
            'trend': trend,
            'pct': pct,
        })

    return render(request, 'kader/monitor.html', {
        'kader': kader,
        'monitor_data': monitor_data,
        'jumlah_tinggi': len(tinggi),
        'jumlah_sedang': len(sedang),
        'jumlah_rendah': len(rendah),
    })

@role_required('kader')
def detail_ibu(request, pk):
    kader = _get_kader(request.user)
    profil = get_object_or_404(IbuProfil, pk=pk, kader=kader)
    history = list(SkriningHasil.objects.filter(ibu=profil).order_by('created_at')[:5])
    latest = SkriningHasil.objects.filter(ibu=profil).first()
    return render(request, 'kader/detail_ibu.html', {
        'kader': kader, 'profil': profil,
        'history': history, 'latest': latest,
    })

@role_required('kader')
def kirim_pesan_ibu(request, pk):
    kader = _get_kader(request.user)
    profil = get_object_or_404(IbuProfil, pk=pk, kader=kader)
    if request.method == 'POST':
        from notifikasi.models import Notifikasi
        judul = request.POST.get('judul', '').strip()
        pesan = request.POST.get('pesan', '').strip()
        tipe  = request.POST.get('tipe', 'pesan')
        if judul and pesan:
            Notifikasi.objects.create(
                penerima=profil.user,
                pengirim=request.user,
                judul=judul, pesan=pesan, tipe=tipe,
            )
            messages.success(request, f'Pesan terkirim ke {profil.user.nama_lengkap}.')
        else:
            messages.error(request, 'Judul dan pesan wajib diisi.')
    return redirect('kader:detail_ibu', pk=pk)


@role_required('kader')
def rujuk_puskesmas(request, pk):
    kader = _get_kader(request.user)
    profil = get_object_or_404(IbuProfil, pk=pk, kader=kader)
    if request.method == 'POST':
        from notifikasi.models import Notifikasi
        from accounts.models import CustomUser
        catatan = request.POST.get('catatan', '').strip()
        petugas_list = CustomUser.objects.filter(role='petugas')
        for petugas in petugas_list:
            Notifikasi.objects.create(
                penerima=petugas,
                pengirim=request.user,
                judul=f'Rujukan: {profil.user.nama_lengkap}',
                pesan=(
                    f'Kader {request.user.nama_lengkap} merujuk ibu hamil '
                    f'{profil.user.nama_lengkap} (skor {profil.get_skor_terakhir()}/55, '
                    f'{profil.get_kategori_risiko()}) ke Puskesmas.'
                    + (f'\n\nCatatan: {catatan}' if catatan else '')
                ),
                tipe='sistem',
            )
        # Beri tahu ibu juga
        Notifikasi.objects.create(
            penerima=profil.user,
            pengirim=request.user,
            judul='Anda Dirujuk ke Puskesmas',
            pesan=(
                f'Kader {request.user.nama_lengkap} telah merujuk Anda ke Puskesmas '
                f'untuk mendapatkan konseling psikolog.'
                + (f'\n\nCatatan: {catatan}' if catatan else '')
            ),
            tipe='sistem',
        )
        messages.success(request, 'Rujukan berhasil dikirim ke Puskesmas.')
    return redirect('kader:detail_ibu', pk=pk)


@role_required('kader')
def jadwal(request):
    kader = _get_kader(request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            jadwal_id = request.POST.get('jadwal_id')
            Jadwal.objects.filter(pk=jadwal_id, kader=kader).delete()
            messages.success(request, 'Jadwal dihapus.')
        elif action == 'create':
            judul = request.POST.get('judul')
            venue = request.POST.get('venue')
            tanggal = request.POST.get('tanggal')
            waktu = request.POST.get('waktu') or None
            if judul and venue and tanggal:
                Jadwal.objects.create(kader=kader, judul=judul, venue=venue, tanggal=tanggal, waktu=waktu)
                messages.success(request, 'Jadwal ditambahkan.')
        return redirect('kader:jadwal')
    jadwal_list = Jadwal.objects.filter(kader=kader).order_by('tanggal')
    return render(request, 'kader/jadwal.html', {'kader': kader, 'jadwal_list': jadwal_list})

@role_required('kader')
def laporan(request):
    kader = _get_kader(request.user)
    ibu_list = list(IbuProfil.objects.filter(kader=kader))
    total = len(ibu_list)
    tinggi = sum(1 for p in ibu_list if p.get_kategori_risiko() == 'Risiko Tinggi')
    sedang = sum(1 for p in ibu_list if p.get_kategori_risiko() == 'Risiko Sedang')
    rendah = sum(1 for p in ibu_list if p.get_kategori_risiko() == 'Risiko Rendah')

    # SVG pie: compute arcs
    from math import pi, cos, sin
    import math
    slices = []
    if total > 0:
        data = [
            {'v': (tinggi/total)*100, 'color': '#ef4444', 'label': f'Risiko Tinggi: {tinggi}'},
            {'v': (sedang/total)*100, 'color': '#1f2937', 'label': f'Risiko Sedang: {sedang}'},
            {'v': (rendah/total)*100, 'color': '#3b82f6', 'label': f'Risiko Rendah: {rendah}'},
        ]
        cx, cy, r = 90, 90, 80
        cumul = 0
        for s in data:
            start = (cumul/100) * 2*math.pi - math.pi/2
            end = ((cumul + s['v'])/100) * 2*math.pi - math.pi/2
            large = 1 if s['v'] > 50 else 0
            x1 = cx + r * math.cos(start)
            y1 = cy + r * math.sin(start)
            x2 = cx + r * math.cos(end)
            y2 = cy + r * math.sin(end)
            path = f'M {cx},{cy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {large} 1 {x2:.1f},{y2:.1f} Z'
            slices.append({'path': path, 'color': s['color'], 'label': s['label']})
            cumul += s['v']

    total_skrining = SkriningHasil.objects.filter(ibu__kader=kader).count()
    all_scores = list(SkriningHasil.objects.filter(ibu__kader=kader).values_list('skor', flat=True))
    avg_skor = round(sum(all_scores)/len(all_scores), 1) if all_scores else 0

    return render(request, 'kader/laporan.html', {
        'kader': kader, 'slices': slices,
        'total_skrining': total_skrining,
        'avg_skor': avg_skor,
        'total': total, 'tinggi': tinggi, 'sedang': sedang, 'rendah': rendah,
    })

@role_required('kader')
def profil(request):
    kader = _get_kader(request.user)
    if request.method == 'POST':
        nama = request.POST.get('nama_lengkap', '').strip()
        if nama:
            request.user.nama_lengkap = nama
            request.user.save()
        kader.posyandu = request.POST.get('posyandu', kader.posyandu)
        kader.wilayah = request.POST.get('wilayah', kader.wilayah)
        if request.POST.get('hapus_foto') == '1':
            if kader.foto:
                kader.foto.delete(save=False)
            kader.foto = None
        elif request.FILES.get('foto'):
            if kader.foto:
                kader.foto.delete(save=False)
            kader.foto = request.FILES['foto']
        kader.save()
        messages.success(request, 'Profil berhasil disimpan.')
        return redirect('kader:profil')
    return render(request, 'kader/profil.html', {'kader': kader})
