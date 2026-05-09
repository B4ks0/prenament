from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.views import role_required
from accounts.models import CustomUser
from ibu.models import IbuProfil, SkriningHasil, ArtikelEdukasi
from kader.models import KaderProfil
from .models import PetugasProfil
import math
from django.utils import timezone
from datetime import timedelta

def _get_petugas(user):
    try:
        return user.petugas_profil
    except PetugasProfil.DoesNotExist:
        return PetugasProfil.objects.create(user=user, nip='', puskesmas='Puskesmas Lansot', jabatan='')

@role_required('petugas')
def beranda(request):
    petugas = _get_petugas(request.user)
    total_ibu = CustomUser.objects.filter(role='ibu').count()
    total_kader = CustomUser.objects.filter(role='kader').count()
    ibu_profils = IbuProfil.objects.all()
    risiko_tinggi = sum(1 for p in ibu_profils if p.get_kategori_risiko() == 'Risiko Tinggi')
    total_skrining = SkriningHasil.objects.count()
    all_scores = list(SkriningHasil.objects.values_list('skor', flat=True))
    avg_skor = round(sum(all_scores)/len(all_scores), 1) if all_scores else 0
    return render(request, 'petugas/beranda.html', {
        'petugas': petugas,
        'total_ibu': total_ibu,
        'total_kader': total_kader,
        'risiko_tinggi': risiko_tinggi,
        'total_skrining': total_skrining,
        'avg_skor': avg_skor,
    })

@role_required('petugas')
def pengguna(request):
    petugas = _get_petugas(request.user)
    tab = request.GET.get('tab', 'ibu')
    search = request.GET.get('q', '')
    if tab == 'kader':
        users = CustomUser.objects.filter(role='kader')
        if search:
            users = users.filter(nama_lengkap__icontains=search)
        kader_data = []
        for u in users:
            try:
                kp = u.kader_profil
                kader_data.append({'user': u, 'profil': kp})
            except:
                kader_data.append({'user': u, 'profil': None})
        return render(request, 'petugas/pengguna.html', {
            'petugas': petugas, 'tab': tab, 'search': search, 'kader_data': kader_data,
        })
    else:
        users = CustomUser.objects.filter(role='ibu')
        if search:
            users = users.filter(nama_lengkap__icontains=search)
        ibu_data = []
        for u in users:
            try:
                profil = u.ibu_profil
                ibu_data.append({'user': u, 'profil': profil, 'kategori': profil.get_kategori_risiko()})
            except:
                ibu_data.append({'user': u, 'profil': None, 'kategori': '-'})
        return render(request, 'petugas/pengguna.html', {
            'petugas': petugas, 'tab': tab, 'search': search, 'ibu_data': ibu_data,
        })

@role_required('petugas')
def statistik(request):
    petugas = _get_petugas(request.user)
    # 6-month bar chart data
    now = timezone.now()
    months_data = []
    month_labels = ['Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    max_val = 1
    for i in range(6):
        month_offset = 5 - i
        start = now - timedelta(days=(month_offset+1)*30)
        end = now - timedelta(days=month_offset*30)
        count = SkriningHasil.objects.filter(created_at__gte=start, created_at__lt=end).count()
        months_data.append(count)
        if count > max_val:
            max_val = count

    # Normalize to percent height
    bars = [{'label': month_labels[i], 'count': months_data[i], 'pct': int((months_data[i]/max_val)*100) if max_val else 10} for i in range(6)]

    # Per-wilayah (kader posyandu)
    kader_list = KaderProfil.objects.all().select_related('user')
    wilayah_data = []
    for k in kader_list:
        ibu_count = IbuProfil.objects.filter(kader=k).count()
        risiko = sum(1 for p in IbuProfil.objects.filter(kader=k) if p.get_kategori_risiko() == 'Risiko Tinggi')
        wilayah_data.append({'kader': k, 'ibu_count': ibu_count, 'risiko_tinggi': risiko})

    return render(request, 'petugas/statistik.html', {
        'petugas': petugas, 'bars': bars, 'wilayah_data': wilayah_data,
    })

@role_required('petugas')
def profil(request):
    petugas = _get_petugas(request.user)
    if request.method == 'POST':
        request.user.nama_lengkap = request.POST.get('nama_lengkap', request.user.nama_lengkap)
        request.user.save()
        petugas.nip = request.POST.get('nip', petugas.nip)
        petugas.puskesmas = request.POST.get('puskesmas', petugas.puskesmas)
        petugas.jabatan = request.POST.get('jabatan', petugas.jabatan)
        petugas.save()
        messages.success(request, 'Profil berhasil disimpan.')
        return redirect('petugas:profil')
    return render(request, 'petugas/profil.html', {'petugas': petugas})


# ── Artikel Edukasi CRUD ─────────────────────────────────────────────
@role_required('petugas')
def artikel_list(request):
    petugas = _get_petugas(request.user)
    q = request.GET.get('q', '')
    artikel = ArtikelEdukasi.objects.all()
    if q:
        artikel = artikel.filter(judul__icontains=q)
    return render(request, 'petugas/artikel_list.html', {
        'petugas': petugas, 'artikel': artikel, 'q': q,
    })


@role_required('petugas')
def artikel_create(request):
    petugas = _get_petugas(request.user)
    KATEGORI = ArtikelEdukasi.KATEGORI_CHOICES
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        ringkasan = request.POST.get('ringkasan', '').strip()
        konten = request.POST.get('konten', '').strip()
        kategori = request.POST.get('kategori', 'umum')
        diterbitkan = request.POST.get('diterbitkan') == '1'
        if judul and konten:
            ArtikelEdukasi.objects.create(
                judul=judul, ringkasan=ringkasan, konten=konten,
                kategori=kategori, diterbitkan=diterbitkan,
                penulis=request.user,
            )
            messages.success(request, 'Artikel berhasil ditambahkan.')
            return redirect('petugas:artikel_list')
        messages.error(request, 'Judul dan konten wajib diisi.')
    return render(request, 'petugas/artikel_form.html', {
        'petugas': petugas, 'KATEGORI': KATEGORI, 'mode': 'create',
    })


@role_required('petugas')
def artikel_edit(request, pk):
    petugas = _get_petugas(request.user)
    artikel = get_object_or_404(ArtikelEdukasi, pk=pk)
    KATEGORI = ArtikelEdukasi.KATEGORI_CHOICES
    if request.method == 'POST':
        artikel.judul = request.POST.get('judul', artikel.judul).strip()
        artikel.ringkasan = request.POST.get('ringkasan', artikel.ringkasan).strip()
        artikel.konten = request.POST.get('konten', artikel.konten).strip()
        artikel.kategori = request.POST.get('kategori', artikel.kategori)
        artikel.diterbitkan = request.POST.get('diterbitkan') == '1'
        artikel.save()
        messages.success(request, 'Artikel berhasil diperbarui.')
        return redirect('petugas:artikel_list')
    return render(request, 'petugas/artikel_form.html', {
        'petugas': petugas, 'artikel': artikel, 'KATEGORI': KATEGORI, 'mode': 'edit',
    })


@role_required('petugas')
def artikel_delete(request, pk):
    if request.method == 'POST':
        artikel = get_object_or_404(ArtikelEdukasi, pk=pk)
        artikel.delete()
        messages.success(request, 'Artikel dihapus.')
    return redirect('petugas:artikel_list')
