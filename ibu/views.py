from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.views import role_required
from .models import IbuProfil, SkriningHasil, SiagaChecklist, ArtikelEdukasi

SIAGA_ITEMS = [
    'Tas siaga berisi obat-obatan pribadi, makanan ringan, air minum, dan dokumen penting (KTP, buku KIA).',
    'Nomor telepon darurat (ambulans, pemadam kebakaran, kader, puskesmas) tersimpan di HP.',
    'Jalur evakuasi dari rumah ke titik kumpul terdekat telah diketahui.',
    'Power bank terisi penuh untuk menjaga komunikasi.',
    'Pakaian ganti yang nyaman untuk 2-3 hari.',
]

QUESTIONS = [
    'Saya cemas tentang persalinan',
    'Saya khawatir tentang rasa sakit kontraksi dan persalinan',
    'Saya takut bayi saya tidak sehat',
    'Saya khawatir tentang perubahan tubuh saya',
]

OPTS = [
    'Sama sekali tidak relevan',
    'Hampir tidak relevan',
    'Kadang-kadang relevan',
    'Cukup relevan',
    'Sangat relevan',
]

ARTICLES = [
    {
        'judul': 'Mengelola Kecemasan Selama Kehamilan',
        'deskripsi': 'Kecemasan adalah hal yang wajar, namun perlu dikelola agar tidak berdampak buruk. Pelajari cara mengenali dan mengatasinya...',
    },
    {
        'judul': 'Tanda Baby Blues vs Depresi Postpartum',
        'deskripsi': 'Kenali perbedaan dan langkah apa yang perlu diambil saat Anda merasa sedih setelah melahirkan...',
    },
    {
        'judul': 'Komunikasi dengan Pasangan Saat Hamil',
        'deskripsi': 'Membangun dukungan emosional dari pasangan sangat penting untuk kesehatan mental Anda...',
    },
]

AUDIO_LIST = [
    {'icon': 'waves', 'judul': 'Latihan Pernapasan Dalam', 'durasi': '5 menit'},
    {'icon': 'muscle', 'judul': 'Relaksasi Otot Progresif', 'durasi': '10 menit'},
    {'icon': 'heart', 'judul': 'Body Scan Mindfulness', 'durasi': '12 menit'},
    {'icon': 'smile', 'judul': 'Visualisasi Tempat Tenang', 'durasi': '8 menit'},
]

AFIRMASI = [
    'Tubuhku kuat dan aku mampu melewati setiap proses kehamilan ini.',
    'Aku mencintai diriku dan bayiku dengan sepenuh hati.',
    'Setiap hari aku semakin dekat dengan momen bahagia bertemu buah hatiku.',
    'Aku tenang, sehat, dan penuh cinta untuk bayiku.',
    'Aku percaya pada kemampuan tubuhku untuk melahirkan dengan aman.',
    'Bayiku tumbuh sehat dan kuat di dalam pelukanku.',
]

def _get_profil(user):
    try:
        return user.ibu_profil
    except IbuProfil.DoesNotExist:
        return IbuProfil.objects.create(user=user)

@role_required('ibu')
def beranda(request):
    profil = _get_profil(request.user)
    latest = SkriningHasil.objects.filter(ibu=profil).first()
    from kader.models import Jadwal
    jadwal_terdekat = None
    if profil.kader:
        jadwal_terdekat = Jadwal.objects.filter(kader=profil.kader).order_by('tanggal').first()
    return render(request, 'ibu/beranda.html', {
        'profil': profil,
        'latest': latest,
        'jadwal_terdekat': jadwal_terdekat,
    })

@role_required('ibu')
def skrining(request):
    profil = _get_profil(request.user)
    if request.method == 'POST':
        answers = []
        for i in range(4):
            val = int(request.POST.get(f'q{i}', 0))
            answers.append(val)
        skor = sum(answers)
        if skor >= 30:
            kategori = 'tinggi'
        elif skor >= 18:
            kategori = 'sedang'
        else:
            kategori = 'rendah'
        SkriningHasil.objects.create(
            ibu=profil, skor=skor, kategori_risiko=kategori,
            jawaban={f'q{i}': v for i, v in enumerate(answers)},
        )
        return redirect('ibu:hasil_skrining')
    history = SkriningHasil.objects.filter(ibu=profil)[:3]
    return render(request, 'ibu/skrining.html', {
        'questions': QUESTIONS, 'opts': OPTS, 'history': history,
    })

@role_required('ibu')
def hasil_skrining(request):
    profil = _get_profil(request.user)
    history = SkriningHasil.objects.filter(ibu=profil)
    latest = history.first()
    return render(request, 'ibu/hasil_skrining.html', {
        'latest': latest, 'history': history[:3],
    })

@role_required('ibu')
def edukasi(request):
    import json
    kategori = request.GET.get('kat', '')
    articles = list(ArtikelEdukasi.objects.filter(diterbitkan=True))
    if kategori:
        articles = [a for a in articles if a.kategori == kategori]
    kategori_list = ArtikelEdukasi.KATEGORI_CHOICES
    articles_json = json.dumps(
        {str(a.pk): {
            'judul': a.judul,
            'konten': a.konten,
            'gambar': a.gambar.url if a.gambar else '',
        } for a in articles},
        ensure_ascii=False,
    )
    return render(request, 'ibu/edukasi.html', {
        'articles': articles,
        'kategori_list': kategori_list,
        'kat_aktif': kategori,
        'articles_json': articles_json,
    })

@role_required('ibu')
def relaksasi(request):
    return render(request, 'ibu/relaksasi.html', {'audio': AUDIO_LIST, 'afirmasi': AFIRMASI})

@role_required('ibu')
def siaga(request):
    profil = _get_profil(request.user)
    if request.method == 'POST':
        item_idx = int(request.POST.get('item', 0))
        obj, created = SiagaChecklist.objects.get_or_create(ibu=profil, nomor_item=item_idx)
        if not created:
            obj.sudah_dicentang = not obj.sudah_dicentang
            obj.save()
        else:
            obj.sudah_dicentang = True
            obj.save()
        return redirect('ibu:siaga')
    checks = {c.nomor_item: c.sudah_dicentang for c in SiagaChecklist.objects.filter(ibu=profil)}
    done = sum(1 for v in checks.values() if v)
    items_with_state = [(i, item, checks.get(i, False)) for i, item in enumerate(SIAGA_ITEMS)]
    return render(request, 'ibu/siaga.html', {
        'items': items_with_state, 'done': done, 'total': len(SIAGA_ITEMS),
    })

@role_required('ibu')
def profil(request):
    profil = _get_profil(request.user)
    if request.method == 'POST':
        nama = request.POST.get('nama_lengkap', '').strip()
        if nama:
            request.user.nama_lengkap = nama
            request.user.save()
        usia = request.POST.get('usia', '').strip()
        if usia.isdigit():
            profil.usia = int(usia)
        profil.alamat = request.POST.get('alamat', profil.alamat).strip()
        uk = request.POST.get('usia_kehamilan', '').strip()
        if uk.isdigit():
            profil.usia_kehamilan = int(uk)
        paritas = request.POST.get('paritas', '').strip()
        if paritas.isdigit():
            profil.paritas = int(paritas)
        profil.save()
        messages.success(request, 'Profil berhasil disimpan.')
        return redirect('ibu:profil')
    return render(request, 'ibu/profil.html', {'profil': profil})
