import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta
from ibu.models import IbuProfil, SkriningHasil, SiagaChecklist, ArtikelEdukasi
from kader.models import KaderProfil, Jadwal
from petugas.models import PetugasProfil

User = get_user_model()


# ── Data pools ────────────────────────────────────────────────────────
NAMA_WANITA = [
    'Citra Dewi', 'Rina Wulandari', 'Lestari Indah', 'Putri Amelia',
    'Sari Rahayu', 'Dewi Anggraini', 'Fitri Handayani', 'Nita Kusuma',
    'Yuni Astuti', 'Hana Pratiwi', 'Mega Sari', 'Diana Permata',
    'Rini Susanti', 'Wulan Cahyani', 'Ayu Lestari', 'Eka Septiani',
    'Novi Kurniawati', 'Lina Marlina', 'Tuti Suryani', 'Endah Wahyuni',
    'Sri Mulyani', 'Ratna Sari', 'Ira Puspita', 'Desi Ratnasari',
    'Maya Safitri', 'Yuli Setiawati', 'Ani Rohmah', 'Budi Astuti',
    'Tina Wahyudi', 'Nurul Hidayah',
]

NAMA_KADER = [
    'Bidan Anisa Rahmat', 'Bidan Maya Sari', 'Bidan Tati Kurniawan',
    'Bidan Yuli Pratiwi', 'Bidan Rina Susanto',
]

POSYANDU = [
    ('Posyandu Melati 1', 'Kelurahan Bahagia'),
    ('Posyandu Melati 2', 'Kelurahan Sejahtera'),
    ('Posyandu Mawar 1', 'Kelurahan Merdeka'),
    ('Posyandu Mawar 2', 'Kelurahan Damai'),
    ('Posyandu Anggrek', 'Kelurahan Harapan'),
]

ALAMAT_POOL = [
    'Jl. Merdeka No. {}', 'Jl. Mawar No. {}', 'Jl. Melati No. {}',
    'Jl. Anggrek No. {}', 'Jl. Kenanga No. {}', 'Jl. Flamboyan No. {}',
    'Jl. Cempaka No. {}', 'Jl. Dahlia No. {}',
]

KELURAHAN_POOL = ['Kel. Bahagia', 'Kel. Sejahtera', 'Kel. Merdeka', 'Kel. Damai', 'Kel. Harapan']

JADWAL_ITEMS = [
    ('Penimbangan & Imunisasi', time(9, 0)),
    ('Kelas Ibu Hamil', time(9, 0)),
    ('Skrining Kesehatan Mental', time(10, 0)),
    ('Pemeriksaan Rutin Kehamilan', time(8, 30)),
    ('Penyuluhan Gizi Ibu Hamil', time(9, 30)),
    ('Senam Hamil', time(8, 0)),
    ('Konseling Menyusui', time(10, 30)),
]

ARTICLES = [
    {
        'judul': 'Mengelola Kecemasan Selama Kehamilan',
        'kategori': 'kecemasan',
        'ringkasan': 'Kecemasan adalah hal yang wajar selama kehamilan, namun perlu dikelola agar tidak berdampak buruk pada ibu dan janin. Pelajari cara mengenali dan mengatasinya.',
        'konten': '''Kecemasan selama kehamilan adalah pengalaman yang sangat umum. Hampir 15-20% ibu hamil mengalami kecemasan yang signifikan. Namun, kecemasan yang berlebihan dapat berdampak negatif pada kesehatan ibu dan perkembangan janin.

Tanda-tanda kecemasan yang perlu diperhatikan:
• Sulit tidur atau sering terbangun malam
• Pikiran yang terus berputar tentang persalinan
• Detak jantung cepat tanpa sebab fisik
• Ketegangan otot yang berlebihan
• Mudah marah atau tersinggung

Cara mengelola kecemasan:
1. Teknik pernapasan dalam — Tarik napas selama 4 hitungan, tahan 4 hitungan, keluarkan selama 6 hitungan.
2. Journaling — Tulis perasaan Anda setiap hari untuk melepaskan beban pikiran.
3. Cerita ke orang terpercaya — Jangan pendam sendiri. Berbagi dengan suami, ibu, atau sahabat.
4. Batasi paparan berita negatif — Pilih informasi yang membangun semangat positif.
5. Bergabung dengan kelas ibu hamil — Bertukar pengalaman dengan sesama ibu hamil.

Ingat: Meminta bantuan adalah tanda kekuatan, bukan kelemahan. Jika kecemasan mengganggu aktivitas sehari-hari, konsultasikan dengan kader atau petugas kesehatan Anda.''',
    },
    {
        'judul': 'Tanda Baby Blues vs Depresi Postpartum',
        'kategori': 'depresi',
        'ringkasan': 'Kenali perbedaan antara baby blues dan depresi postpartum, serta langkah yang perlu diambil saat Anda merasa sedih setelah melahirkan.',
        'konten': '''Setelah melahirkan, banyak ibu mengalami perubahan suasana hati yang drastis. Penting untuk membedakan antara baby blues yang normal dan depresi postpartum yang memerlukan penanganan khusus.

Baby Blues (Normal):
• Muncul 2-3 hari setelah melahirkan
• Berlangsung maksimal 2 minggu
• Gejala: mudah menangis, sensitif, lelah, khawatir berlebihan
• Hilang dengan sendirinya seiring adaptasi hormonal

Depresi Postpartum (Perlu Penanganan):
• Muncul kapan saja dalam setahun pertama
• Berlangsung lebih dari 2 minggu
• Gejala lebih berat: tidak mau menyusui, merasa tidak terikat dengan bayi, pikiran untuk menyakiti diri sendiri
• Memerlukan bantuan profesional

Langkah yang harus dilakukan:
1. Ceritakan perasaan Anda kepada suami atau keluarga dekat.
2. Istirahat cukup — mintalah bantuan untuk merawat bayi secara bergantian.
3. Jangan terisolasi — terima kunjungan keluarga dan teman.
4. Hubungi kader atau bidan jika gejala berlangsung lebih dari 2 minggu.
5. Jangan ragu ke puskesmas untuk mendapatkan rujukan psikolog.

Anda tidak sendirian. Depresi postpartum dapat disembuhkan dengan penanganan yang tepat.''',
    },
    {
        'judul': 'Komunikasi dengan Pasangan Saat Hamil',
        'kategori': 'umum',
        'ringkasan': 'Membangun dukungan emosional dari pasangan sangat penting untuk kesehatan mental ibu hamil. Pelajari cara berkomunikasi yang efektif.',
        'konten': '''Kehamilan bukan hanya perjalanan seorang ibu — ini adalah perjalanan bersama. Dukungan pasangan terbukti secara ilmiah mengurangi risiko depresi dan kecemasan pada ibu hamil hingga 40%.

Mengapa komunikasi penting?
Selama kehamilan, perubahan hormonal membuat ibu lebih sensitif secara emosional. Tanpa komunikasi yang baik, pasangan bisa salah memahami perubahan perilaku ini, yang justru menambah beban stres.

Tips komunikasi efektif dengan pasangan:

1. Jadwalkan waktu bicara harian
Sisihkan 15-20 menit setiap malam untuk berbagi cerita tentang hari Anda masing-masing tanpa gangguan gadget.

2. Gunakan "saya merasa" bukan "kamu selalu"
Contoh: "Saya merasa kesepian saat kamu pulang larut" lebih baik dari "Kamu selalu pulang larut dan tidak peduli."

3. Minta bantuan secara spesifik
Jangan berharap pasangan bisa menebak kebutuhan Anda. Katakan dengan jelas: "Malam ini aku butuh punggungku dipijat" atau "Aku butuh kamu memasak makan malam."

4. Libatkan pasangan dalam persiapan kelahiran
Ajak pasangan ke pemeriksaan ANC, kelas persiapan persalinan, dan diskusi nama bayi.

5. Ekspresikan apresiasi
Ucapkan terima kasih atas hal kecil yang dilakukan pasangan. Apresiasi membangun siklus positif dalam hubungan.

Keluarga yang solid adalah fondasi terbaik untuk menyambut buah hati.''',
    },
    {
        'judul': 'Nutrisi Penting untuk Ibu Hamil dan Janin',
        'kategori': 'nutrisi',
        'ringkasan': 'Asupan nutrisi yang tepat selama kehamilan sangat menentukan kesehatan ibu dan perkembangan optimal janin.',
        'konten': '''Nutrisi selama kehamilan adalah investasi terbaik untuk masa depan anak Anda. Berikut panduan nutrisi lengkap untuk ibu hamil:

Trimester 1 (Minggu 1-12):
Fokus pada asam folat (400-800 mcg/hari) untuk mencegah cacat tabung saraf. Sumber: sayuran hijau, kacang-kacangan, jeruk.

Trimester 2 (Minggu 13-27):
Kebutuhan kalori meningkat 340 kkal/hari. Tingkatkan zat besi (27 mg/hari) untuk mencegah anemia. Sumber: daging merah, bayam, tahu tempe.

Trimester 3 (Minggu 28-40):
Kebutuhan kalsium 1000 mg/hari untuk pembentukan tulang janin. Sumber: susu, keju, ikan teri, kacang almond.

Nutrisi kritis yang tidak boleh diabaikan:
• Zat besi — cegah anemia, penting untuk transport oksigen ke janin
• Kalsium — pembentukan tulang dan gigi janin
• Asam folat — mencegah cacat lahir pada sistem saraf
• DHA/Omega-3 — perkembangan otak janin
• Protein — 71 gram per hari, sumber: telur, ikan, daging, kacang-kacangan
• Vitamin D — bantu penyerapan kalsium

Makanan yang harus dihindari:
X Ikan tinggi merkuri (hiu, todak, king mackerel)
X Daging dan telur mentah/setengah matang
X Susu tidak dipasteurisasi
X Kafein berlebihan (maksimal 200 mg/hari)
X Minuman beralkohol

Tips praktis: Makan 5-6 porsi kecil per hari lebih baik dari 3 porsi besar untuk mengurangi mual dan menjaga kadar gula darah stabil.''',
    },
    {
        'judul': 'Teknik Relaksasi untuk Ibu Hamil',
        'kategori': 'kecemasan',
        'ringkasan': 'Relaksasi bukan sekadar istirahat — ini adalah terapi aktif yang terbukti menurunkan kecemasan, tekanan darah, dan nyeri persalinan.',
        'konten': '''Penelitian menunjukkan ibu hamil yang rutin melakukan relaksasi memiliki pengalaman persalinan yang lebih baik dan risiko komplikasi yang lebih rendah.

1. Pernapasan Diafragma
Teknik dasar yang bisa dilakukan kapan saja:
• Duduk nyaman, letakkan satu tangan di dada, satu di perut
• Tarik napas lewat hidung, rasakan perut mengembang (bukan dada)
• Tahan 2 hitungan
• Hembus perlahan lewat mulut selama 6 hitungan
• Ulangi 10 kali, 3x sehari

2. Relaksasi Otot Progresif
• Mulai dari kaki — kencangkan otot betis 5 detik, lalu lepaskan
• Naik ke paha, perut, bahu, tangan, dan wajah
• Rasakan perbedaan antara tegang dan rileks
• Durasi: 15-20 menit sebelum tidur

3. Visualisasi Positif
Bayangkan tempat yang damai: pantai, pegunungan, atau rumah masa kecil. Bayangkan detail seperti suara angin, aroma bunga, atau hangatnya sinar matahari. Lakukan selama 10 menit.

4. Prenatal Yoga
Gerakan ringan yang memperkuat otot inti, meningkatkan fleksibilitas, dan mempersiapkan tubuh untuk persalinan. Ikuti kelas yang dipandu instruktur bersertifikat.

5. Mindfulness
Fokus pada momen sekarang tanpa menghakimi. Saat makan, rasakan tekstur dan rasa makanan. Saat berjalan, rasakan setiap langkah. Latih selama 5 menit sehari.

Jadwalkan waktu relaksasi seperti Anda menjadwalkan kunjungan dokter — itu sama pentingnya.''',
    },
    {
        'judul': 'Persiapan Mental Menghadapi Persalinan',
        'kategori': 'persalinan',
        'ringkasan': 'Ketakutan akan persalinan adalah normal, tetapi dengan persiapan yang tepat, Anda bisa menghadapinya dengan lebih percaya diri dan tenang.',
        'konten': '''Tokophobia (ketakutan berlebihan terhadap persalinan) dialami oleh 14% ibu hamil. Namun, ketakutan ini bisa diatasi dengan pengetahuan dan persiapan yang tepat.

Mengapa ibu takut melahirkan?
• Rasa sakit kontraksi dan persalinan
• Takut terjadi komplikasi
• Pengalaman buruk sebelumnya (untuk multigravida)
• Informasi yang tidak akurat dari media sosial

Membangun kepercayaan diri:
1. Edukasi diri dengan sumber terpercaya
Ikuti kelas persiapan persalinan di puskesmas atau rumah sakit. Pengetahuan yang benar mengurangi ketakutan secara signifikan.

2. Buat birth plan
Tuliskan preferensi persalinan Anda: siapa yang ingin ada, posisi melahirkan yang diinginkan, metode manajemen nyeri. Ini memberi rasa kontrol.

3. Latih teknik manajemen nyeri
Pernapasan Lamaze, water birth, TENS — pelajari opsi yang tersedia dan latih sebelum waktunya.

4. Bangun tim dukungan yang solid
Pastikan suami/pendamping memahami peran mereka. Kehadiran orang yang dicintai terbukti mengurangi persepsi rasa sakit.

5. Percayai tubuh Anda
Tubuh wanita dirancang untuk melahirkan. Jutaan ibu sebelum Anda telah melaluinya. Anda lebih kuat dari yang Anda kira.

6. Bicarakan ketakutan dengan bidan
Bidan Anda adalah mitra — ceritakan semua kekhawatiran Anda. Tidak ada yang terlalu sepele untuk didiskusikan.

Ingat: Tujuan akhirnya bukan proses yang sempurna, tapi ibu dan bayi yang sehat dan selamat.''',
    },
    {
        'judul': 'Perawatan Bayi Baru Lahir: Panduan Praktis',
        'kategori': 'bayi',
        'ringkasan': 'Merawat bayi baru lahir bisa terasa overwhelming. Panduan ini membantu Anda memahami kebutuhan dasar bayi dan membangun ikatan yang kuat.',
        'konten': '''Hari-hari pertama bersama bayi baru lahir adalah pengalaman yang luar biasa sekaligus menantang. Berikut panduan praktis yang perlu Anda ketahui:

Menyusui ASI:
• Mulai dalam 1 jam pertama setelah lahir (inisiasi menyusu dini)
• ASI eksklusif selama 6 bulan pertama — tidak perlu tambahan air atau makanan lain
• Susui setiap 2-3 jam atau saat bayi menunjukkan tanda lapar
• Tanda bayi cukup ASI: buang air kecil 6-8x/hari, berat badan naik

Memandikan Bayi:
• Tunggu 24 jam setelah lahir sebelum memandikan (vernix melindungi kulit)
• Air hangat suam-suam kuku (37°C)
• Cukup 2-3x seminggu untuk bayi baru lahir
• Selalu pegang kepala bayi dengan aman

Tidur Bayi:
• Bayi baru lahir tidur 16-18 jam per hari
• Posisi tidur: telentang (mengurangi risiko SIDS)
• Pastikan kasur keras dan tidak ada bantal/selimut tebal
• Kamar bertemperatur nyaman (20-22°C)

Mengenali Tanda Bahaya:
🚨 Segera ke dokter jika:
• Demam >38°C pada bayi <3 bulan
• Tidak mau menyusu lebih dari 4-6 jam
• Tali pusat berbau atau bernanah
• Kuning (jaundice) yang menyebar ke tubuh
• Napas cepat >60x/menit

Membangun Ikatan (Bonding):
• Skin-to-skin contact di awal kelahiran
• Bicara dan nyanyikan lagu lembut
• Kontak mata saat menyusui
• Gendongan (babywearing) yang aman

Percayai insting Anda. Tidak ada panduan yang lebih baik dari kasih sayang seorang ibu.''',
    },
    {
        'judul': 'Anemia pada Ibu Hamil: Kenali dan Cegah',
        'kategori': 'nutrisi',
        'ringkasan': 'Anemia adalah masalah kesehatan paling umum pada ibu hamil di Indonesia. Kenali gejalanya dan cara mencegahnya sejak dini.',
        'konten': '''Data Kemenkes RI menunjukkan 48,9% ibu hamil di Indonesia mengalami anemia. Kondisi ini dapat berdampak serius pada ibu dan janin jika tidak ditangani.

Apa itu anemia pada kehamilan?
Anemia terjadi ketika kadar hemoglobin (Hb) dalam darah di bawah normal. Pada ibu hamil, batas normal Hb adalah ≥11 g/dL.

Penyebab umum:
• Kekurangan zat besi (paling sering)
• Kekurangan vitamin B12 atau asam folat
• Kehilangan darah (perdarahan)
• Penyakit kronis

Gejala yang perlu diwaspadai:
• Mudah lelah dan lemas
• Pucat pada kulit, bibir, dan kuku
• Pusing atau kepala terasa ringan
• Sesak napas saat beraktivitas ringan
• Jantung berdebar-debar
• Sulit berkonsentrasi

Dampak jika tidak ditangani:
!️ Pada ibu: perdarahan saat persalinan, infeksi, komplikasi jantung
!️ Pada janin: BBLR (berat bayi lahir rendah), prematur, gangguan perkembangan

Pencegahan dan pengobatan:
1. Konsumsi tablet tambah darah (TTD) minimal 90 tablet selama kehamilan — ambil dari puskesmas/posyandu GRATIS
2. Makan makanan kaya zat besi: daging merah, hati sapi, bayam, kacang hijau, ikan
3. Minum tablet zat besi dengan jus jeruk (vitamin C membantu penyerapan)
4. Hindari minum teh/kopi 1 jam sebelum/sesudah makan tablet zat besi
5. Pemeriksaan Hb minimal 2x selama kehamilan

Jangan tunggu sampai gejala parah — periksa Hb Anda saat kunjungan ANC berikutnya.''',
    },
    {
        'judul': 'Olahraga Aman Selama Kehamilan',
        'kategori': 'umum',
        'ringkasan': 'Olahraga selama kehamilan bukan hanya aman — ini sangat dianjurkan untuk kesehatan ibu dan janin. Ketahui jenis olahraga yang tepat.',
        'konten': '''Olahraga selama kehamilan yang dilakukan dengan benar terbukti mengurangi risiko komplikasi, mempercepat pemulihan pasca persalinan, dan meningkatkan mood ibu hamil.

Manfaat olahraga saat hamil:
OK Mengurangi nyeri punggung bawah
OK Mencegah kenaikan berat badan berlebihan
OK Mengurangi risiko diabetes gestasional
OK Memperbaiki kualitas tidur
OK Mengurangi kecemasan dan depresi
OK Memperkuat otot untuk persalinan

Olahraga yang dianjurkan:

1. Jalan Kaki (Semua trimester)
30 menit, 5 hari seminggu. Mulai dari 10 menit jika belum terbiasa. Gunakan sepatu yang nyaman.

2. Renang (Semua trimester)
Olahraga terbaik untuk ibu hamil — mengapung mengurangi tekanan pada sendi. Gaya bebas dan punggung sangat disarankan.

3. Prenatal Yoga
Meningkatkan keseimbangan, fleksibilitas, dan pernapasan. Cari kelas khusus ibu hamil.

4. Senam Hamil
Dirancang khusus untuk memperkuat otot dasar panggul dan mempersiapkan tubuh untuk persalinan.

5. Bersepeda Statis
Aman dan efektif, terutama jika Anda terbiasa bersepeda sebelum hamil.

Olahraga yang HARUS dihindari:
X Olahraga kontak (basket, sepak bola, tinju)
X Olahraga dengan risiko jatuh tinggi (berkuda, ski)
X Menyelam
X Olahraga di ketinggian tinggi
X Sit-up atau crunch (setelah trimester 1)

Tanda harus berhenti olahraga segera:
🚨 Perdarahan vagina, kontraksi, sesak napas berat, nyeri dada, kepala berputar

Konsultasikan dengan bidan atau dokter sebelum memulai program olahraga baru.''',
    },
    {
        'judul': 'Mengenal Tanda Bahaya Kehamilan',
        'kategori': 'persalinan',
        'ringkasan': 'Kenali 7 tanda bahaya kehamilan yang harus segera mendapat penanganan medis. Pengetahuan ini bisa menyelamatkan nyawa ibu dan bayi.',
        'konten': '''Setiap ibu hamil wajib mengetahui tanda bahaya kehamilan. Pengenalan dini dan penanganan cepat dapat mencegah komplikasi yang mengancam jiwa.

7 Tanda Bahaya Kehamilan (SEGERA KE FASILITAS KESEHATAN):

1. 🩸 Perdarahan dari vagina
Perdarahan apapun selama kehamilan — ringan atau berat — harus segera diperiksa. Bisa menandakan plasenta previa, solusio plasenta, atau ancaman keguguran.

2. 😮‍💨 Sesak napas hebat
Napas yang sangat sulit bisa menandakan emboli paru atau masalah jantung.

3. 🤢 Muntah terus-menerus dan tidak bisa makan/minum
Hiperemesis gravidarum dapat menyebabkan dehidrasi berat yang berbahaya.

4. 🌡️ Demam tinggi >38°C
Bisa menandakan infeksi serius yang membahayakan ibu dan janin.

5. 👀 Gangguan penglihatan (kabur, melihat bintang-bintang)
Tanda preeklamsia — tekanan darah tinggi berbahaya yang bisa berkembang menjadi eklamsia.

6. 🤕 Sakit kepala hebat yang tidak hilang
Kombinasi sakit kepala berat + pembengkakan tangan/wajah = waspadai preeklamsia.

7. 💧 Keluar cairan dari vagina sebelum waktunya
Bisa menandakan ketuban pecah dini yang meningkatkan risiko infeksi dan kelahiran prematur.

Tanda bahaya TAMBAHAN:
• Gerakan janin berkurang/tidak ada (setelah usia 28 minggu)
• Bengkak mendadak pada wajah, tangan, dan kaki
• Nyeri perut hebat dan terus-menerus

Siapkan selalu:
📋 Kartu ANC/buku KIA
💰 Biaya persalinan (atau pastikan BPJS aktif)
🚗 Transportasi siap 24 jam
📞 Nomor darurat puskesmas/rumah sakit tersimpan di HP

"Lebih baik periksa dan tidak ada masalah, daripada tidak periksa dan terlambat."''',
    },
    {
        'judul': 'Dukungan Sosial untuk Ibu Hamil',
        'kategori': 'umum',
        'ringkasan': 'Jaringan dukungan sosial yang kuat terbukti mengurangi risiko depresi dan kecemasan selama kehamilan. Pelajari cara membangunnya.',
        'konten': '''Penelitian Harvard School of Public Health membuktikan: ibu hamil dengan jaringan dukungan sosial yang kuat mengalami 60% lebih sedikit komplikasi kehamilan dibanding yang merasa terisolasi.

Mengapa dukungan sosial penting?
Dukungan sosial tidak hanya baik untuk mental — ini mempengaruhi fisik. Ketika Anda merasa didukung, tubuh memproduksi lebih banyak oksitosin (hormon cinta) dan lebih sedikit kortisol (hormon stres).

Membangun jaringan dukungan:

1. Keluarga Inti
Libatkan suami secara aktif dalam persiapan kehamilan. Minta ibu atau mertua untuk berbagi pengalaman positif mereka. Batasi paparan cerita menakutkan dari keluarga yang "suka menakut-nakuti."

2. Komunitas Ibu Hamil
Bergabunglah dengan kelas ibu hamil di puskesmas atau posyandu. Berbagi pengalaman dengan sesama ibu hamil yang memiliki usia kehamilan serupa sangat menenangkan.

3. Teman Sebaya
Cari teman yang telah atau sedang hamil. Mereka memahami apa yang Anda rasakan dari pengalaman langsung.

4. Tenaga Kesehatan
Bidan dan kader posyandu Anda bukan hanya pemeriksa fisik — mereka adalah bagian dari sistem dukungan Anda. Jangan ragu menceritakan kekhawatiran emosional.

5. Komunitas Online (dengan bijak)
Grup ibu hamil di media sosial bisa jadi sumber dukungan, tapi selektif. Ikuti grup yang positif dan berbasis informasi medis yang akurat.

Cara meminta bantuan:
Banyak ibu hamil enggan meminta bantuan karena merasa merepotkan. Ingat: orang-orang yang peduli pada Anda INGIN membantu — mereka hanya perlu diberitahu caranya.

Katakan: "Aku butuh bantuan memasak 3x seminggu" atau "Maukah kamu menemani aku ke pemeriksaan?"

Jadilah bagian dari komunitas, dan komunitas akan menjaga Anda.''',
    },
    {
        'judul': 'Peran Suami dalam Mendukung Kehamilan',
        'kategori': 'umum',
        'ringkasan': 'Suami adalah mitra terpenting dalam perjalanan kehamilan. Panduan ini membantu suami memahami cara terbaik mendukung istri.',
        'konten': '''Kehadiran dan keterlibatan suami selama kehamilan bukan sekadar formalitas — ini adalah faktor yang secara signifikan mempengaruhi kesehatan mental dan fisik istri.

Data menunjukkan: Ibu hamil dengan suami yang terlibat aktif mengalami 50% lebih sedikit gejala depresi dan melaporkan kepuasan hidup yang lebih tinggi.

Peran suami yang paling dibutuhkan:

Dukungan Emosional:
• Dengarkan tanpa menghakimi saat istri bercerita
• Validasi perasaan istri: "Aku mengerti itu sulit bagimu"
• Kurangi stres di rumah — ciptakan lingkungan yang tenang
• Ekspresikan cinta secara verbal dan fisik (pelukan, pijatan)

Dukungan Praktis:
• Bantu pekerjaan rumah tanpa diminta
• Antar jemput ke pemeriksaan kehamilan
• Siapkan makanan sehat
• Bantu menyiapkan perlengkapan bayi

Keterlibatan dalam Kehamilan:
• Ikut USG dan pemeriksaan ANC
• Baca buku/artikel tentang kehamilan bersama
• Bicara dan sentuh perut istri — bayi dapat mendengar suara ayah sejak usia 18 minggu
• Ikuti kelas persiapan persalinan

Mempersiapkan Persalinan:
• Pelajari tanda-tanda awal persalinan
• Siapkan tas rumah sakit bersama
• Rencanakan rute dan transportasi ke fasilitas kesehatan
• Jadikan diri sebagai "doula" — pendamping persalinan terbaik

Hal yang perlu dihindari:
X Membandingkan istri dengan wanita lain
X Meremehkan keluhan: "Lebay ah, cuma mual"
X Terlalu banyak memberi saran tanpa diminta
X Mengabaikan perubahan emosi istri

Kehadiran Anda adalah hadiah terbesar yang bisa Anda berikan kepada istri dan calon anak Anda.''',
    },
    {
        'judul': 'ASI Eksklusif: Manfaat dan Cara Sukses Menyusui',
        'kategori': 'bayi',
        'ringkasan': 'ASI eksklusif selama 6 bulan adalah standar emas nutrisi bayi. Pelajari manfaatnya dan strategi sukses menyusui.',
        'konten': '''WHO dan UNICEF menyatakan ASI eksklusif sebagai intervensi kesehatan tunggal yang paling efektif untuk menyelamatkan nyawa bayi. Namun hanya 40% bayi Indonesia mendapat ASI eksklusif 6 bulan.

Apa itu ASI Eksklusif?
Memberikan hanya ASI — tanpa susu formula, air, atau makanan lain — selama 6 bulan pertama kehidupan. Setelah 6 bulan, lanjutkan ASI bersama MPASI hingga usia 2 tahun.

Manfaat ASI untuk Bayi:
🍼 Nutrisi sempurna yang berubah sesuai kebutuhan bayi
🛡️ Antibodi kuat — melindungi dari infeksi, alergi, dan penyakit
🧠 Asam lemak DHA dan ARA untuk perkembangan otak optimal
❤️ Membangun ikatan emosional yang kuat dengan ibu

Manfaat untuk Ibu:
💪 Membantu rahim kembali ke ukuran normal lebih cepat
⚖️ Membakar 300-500 kalori/hari — membantu turunkan berat badan pasca melahirkan
🩺 Mengurangi risiko kanker payudara dan ovarium
😴 ASI mengandung hormon yang membantu ibu tidur lebih nyenyak

Strategi Sukses Menyusui:

Persiapan Sebelum Lahir:
• Ikuti kelas laktasi di puskesmas/RS
• Periksa kondisi puting (datar/tenggelam perlu penanganan khusus)
• Siapkan mental — menyusui perlu waktu untuk dipelajari

Setelah Lahir:
• Mulai dalam 1 jam pertama (IMD)
• Susui sesering mungkin — minimal 8-12x/24 jam di awal
• Pastikan pelekatan (latch) yang benar untuk mencegah nyeri

Mengatasi Masalah Umum:
Putting lecet → Perbaiki posisi pelekatan, oleskan ASI pada puting setelah menyusui
Produksi kurang → Susui lebih sering, minum cukup air (3 liter/hari), istirahat cukup
Payudara bengkak → Susui lebih sering, kompres hangat sebelum menyusui

Dukungan untuk keberhasilan menyusui:
Bergabunglah dengan kelompok pendukung ASI di posyandu. Ibu yang berhasil menyusui adalah motivator terbaik untuk ibu yang baru memulai.

"Setiap tetes ASI adalah investasi terbaik untuk masa depan anak Anda."''',
    },
    {
        'judul': 'Mengatasi Insomnia selama Kehamilan',
        'kategori': 'kecemasan',
        'ringkasan': 'Sulit tidur adalah keluhan yang sangat umum pada ibu hamil, terutama di trimester ketiga. Pelajari penyebab dan solusinya.',
        'konten': '''78% ibu hamil mengalami gangguan tidur di beberapa titik selama kehamilan. Kurang tidur bukan hanya melelahkan — ini mempengaruhi produksi hormon, sistem imun, dan suasana hati.

Mengapa ibu hamil susah tidur?

Fisik:
• Perut besar yang sulit dicari posisi nyaman
• Sering buang air kecil di malam hari
• Kaki kram atau sindrom kaki gelisah
• Mulas/refluks asam lambung
• Sesak napas karena diafragma tertekan

Psikologis:
• Kekhawatiran tentang persalinan dan masa depan
• Pikiran yang tidak bisa berhenti berputar
• Kecemasan umum yang meningkat di malam hari

Strategi mengatasi insomnia kehamilan:

Posisi Tidur Optimal:
Tidur miring ke kiri (Left Lateral Decubitus) adalah posisi terbaik di trimester 2 dan 3 karena meningkatkan aliran darah ke janin. Gunakan bantal kehamilan (pregnancy pillow) untuk menyangga perut dan punggung.

Rutinitas Tidur yang Baik:
• Tidur dan bangun di jam yang sama setiap hari
• Matikan layar (HP, TV) 1 jam sebelum tidur — cahaya biru mengganggu melatonin
• Mandi air hangat 30 menit sebelum tidur
• Kamar sejuk, gelap, dan hening

Mengatasi Kram Kaki:
Regangkan betis sebelum tidur: berdiri tegak, tahan 30 detik. Pastikan cukup kalsium dan magnesium.

Mengurangi Buang Air Kecil Malam:
Kurangi minum 2 jam sebelum tidur (tapi jangan kurangi total asupan harian).

Menenangkan Pikiran:
• Tuliskan kekhawatiran di jurnal sebelum tidur — "keluarkan" dari kepala ke kertas
• Teknik pernapasan 4-7-8: tarik napas 4 hitungan, tahan 7, keluarkan 8
• Dengarkan musik lembut atau white noise

Jika tetap tidak bisa tidur selama 20 menit, bangun dan lakukan aktivitas tenang (membaca, mendengarkan musik) sampai mengantuk. Jangan berbaring terjaga — ini melatih otak mengasosiasikan tempat tidur dengan insomnia.''',
    },
    {
        'judul': 'Kesehatan Mental Pasca Bencana untuk Ibu Hamil',
        'kategori': 'kecemasan',
        'ringkasan': 'Ibu hamil adalah kelompok rentan saat bencana. Panduan ini membantu menjaga kesehatan mental dan fisik saat menghadapi situasi darurat.',
        'konten': '''Ibu hamil menghadapi tantangan ganda saat bencana — kekhawatiran tentang diri sendiri dan bayinya. Penelitian pasca bencana menunjukkan ibu hamil 3x lebih rentan mengalami PTSD dibanding populasi umum.

Respons normal terhadap bencana:
Merasa takut, sedih, marah, atau mati rasa adalah respons normal terhadap situasi tidak normal. Ini bukan kelemahan — ini adalah cara otak memproses trauma.

Gejala yang perlu diwaspadai:
• Flashback atau mimpi buruk berulang tentang kejadian bencana
• Menghindari hal-hal yang mengingatkan pada bencana
• Perasaan mati rasa atau terputus dari sekitar
• Hypervigilance — selalu waspada berlebihan
• Gejala berlangsung lebih dari 1 bulan

Strategi pemulihan psikologis:

1. Kembali ke Rutinitas
Rutinitas memberikan rasa kontrol dan normalcy. Bahkan rutinitas sederhana seperti jadwal makan dan tidur membantu otak pulih.

2. Koneksi Sosial
Jangan isolasi diri. Kebersamaan dengan orang-orang yang dicintai adalah balsem terkuat untuk trauma.

3. Informasi yang Terkontrol
Batasi menonton berita bencana. Cukup 1-2x sehari untuk update penting. Terlalu banyak paparan memperburuk stres.

4. Perhatikan Janin
Stres ekstrem mempengaruhi hormon kortisol yang sampai ke janin. Teknik relaksasi aktif — bahkan di pengungsian — adalah bentuk perlindungan terbaik untuk bayi Anda.

5. Cari Bantuan Profesional
Jika gejala berat, ceritakan ke tenaga kesehatan di pos pengungsian. Layanan kesehatan jiwa tersedia gratis di fasilitas kesehatan pemerintah.

Persiapan tas siaga:
OK Buku KIA dan kartu ANC
OK Suplemen zat besi dan vitamin kehamilan
OK Air minum yang cukup
OK Makanan bergizi portabel
OK Nomor darurat puskesmas dan bidan tersimpan

Anda tidak harus menjadi kuat sendirian. Terimalah bantuan yang ditawarkan.''',
    },
]


class Command(BaseCommand):
    help = 'Seed dummy data masif untuk PRENAMENT'

    def handle(self, *args, **options):
        self.stdout.write('Menghapus data lama...')
        User.objects.all().delete()

        random.seed(42)

        # ── 1. Petugas ──────────────────────────────────────────────
        self.stdout.write('Membuat petugas...')
        petugas_data = [
            ('sari', 'dr. Sari Putri', '198501012010012001', 'Kepala Puskesmas'),
            ('budi', 'dr. Budi Santoso', '197803152005011002', 'Dokter Umum'),
            ('nani', 'Nani Suryani, S.Kep', '199002202015022003', 'Perawat Koordinator'),
        ]
        petugas_users = []
        for username, nama, nip, jabatan in petugas_data:
            u = User.objects.create_user(
                username=username, password='pass123',
                nama_lengkap=nama, role='petugas', email=f'{username}@puskesmas.id'
            )
            PetugasProfil.objects.create(
                user=u, nip=nip, puskesmas='Puskesmas Lansot', jabatan=jabatan
            )
            petugas_users.append(u)
            self.stdout.write(f'  OK {nama}')

        penulis_utama = petugas_users[0]

        # ── 2. Artikel Edukasi ───────────────────────────────────────
        self.stdout.write('Membuat artikel edukasi...')
        for art in ARTICLES:
            ArtikelEdukasi.objects.create(
                judul=art['judul'],
                kategori=art['kategori'],
                ringkasan=art['ringkasan'],
                konten=art['konten'],
                penulis=penulis_utama,
                diterbitkan=True,
            )
        # 1 draft artikel
        ArtikelEdukasi.objects.create(
            judul='Persiapan MPASI untuk Bayi 6 Bulan [DRAFT]',
            kategori='bayi',
            ringkasan='Panduan lengkap memulai MPASI yang aman dan bernutrisi.',
            konten='Artikel ini sedang dalam proses penulisan...',
            penulis=petugas_users[1],
            diterbitkan=False,
        )
        self.stdout.write(f'  OK {len(ARTICLES) + 1} artikel dibuat')

        # ── 3. Kader ────────────────────────────────────────────────
        self.stdout.write('Membuat kader...')
        kader_profils = []
        for i, (nama, (posyandu, wilayah)) in enumerate(zip(NAMA_KADER, POSYANDU)):
            username = f'kader{i+1}'
            u = User.objects.create_user(
                username=username, password='pass123',
                nama_lengkap=nama, role='kader', email=f'{username}@posyandu.id'
            )
            kp = KaderProfil.objects.create(user=u, posyandu=posyandu, wilayah=wilayah)
            kader_profils.append(kp)
            self.stdout.write(f'  OK {nama} — {posyandu}')

        # alias untuk backward-compat (citra/anisa/sari tetap tersedia)
        User.objects.filter(username='kader1').update(username='anisa')

        # ── 4. Jadwal Kader ─────────────────────────────────────────
        self.stdout.write('Membuat jadwal...')
        jadwal_dates = [
            date(2025, 12, 15), date(2026, 1, 12), date(2026, 1, 26),
            date(2026, 2,  9),  date(2026, 2, 23), date(2026, 3,  9),
            date(2026, 3, 23),
        ]
        total_jadwal = 0
        for kp in kader_profils:
            picked = random.sample(JADWAL_ITEMS, k=min(4, len(JADWAL_ITEMS)))
            for (judul, waktu), d in zip(picked, jadwal_dates[:len(picked)]):
                Jadwal.objects.create(
                    kader=kp, judul=judul, venue=kp.posyandu,
                    tanggal=d, waktu=waktu
                )
                total_jadwal += 1
        self.stdout.write(f'  OK {total_jadwal} jadwal dibuat')

        # ── 5. Ibu Hamil ─────────────────────────────────────────────
        self.stdout.write('Membuat ibu hamil...')

        # Data preset (untuk akun yang bisa login dengan nama mudah)
        preset_ibu = [
            {
                'username': 'citra', 'nama_lengkap': 'Citra Dewi',
                'usia': 28, 'usia_kehamilan': 32, 'paritas': 0,
                'kader_idx': 0,
                'scores': [37, 38, 37, 35, 32, 30],
            },
            {
                'username': 'rina', 'nama_lengkap': 'Rina Wulandari',
                'usia': 25, 'usia_kehamilan': 24, 'paritas': 1,
                'kader_idx': 0,
                'scores': [22, 24, 26, 23, 22, 20],
            },
            {
                'username': 'lestari', 'nama_lengkap': 'Lestari Indah',
                'usia': 30, 'usia_kehamilan': 16, 'paritas': 2,
                'kader_idx': 1,
                'scores': [12, 14, 16, 15, 13, 10],
            },
            {
                'username': 'putri', 'nama_lengkap': 'Putri Amelia',
                'usia': 22, 'usia_kehamilan': 28, 'paritas': 0,
                'kader_idx': 1,
                'scores': [14, 13, 15, 14, 12, 11],
            },
        ]

        nama_remaining = [n for n in NAMA_WANITA if n not in [d['nama_lengkap'] for d in preset_ibu]]
        random.shuffle(nama_remaining)

        all_ibu_created = 0

        def make_ibu(username, nama, usia, usia_kehamilan, paritas, kader, scores):
            nonlocal all_ibu_created
            alamat_tmpl = random.choice(ALAMAT_POOL)
            kel = random.choice(KELURAHAN_POOL)
            alamat = alamat_tmpl.format(random.randint(1, 99)) + ', ' + kel
            u = User.objects.create_user(
                username=username, password='pass123',
                nama_lengkap=nama, role='ibu', email=f'{username}@prenament.id'
            )
            profil = IbuProfil.objects.create(
                user=u, usia=usia, alamat=alamat,
                usia_kehamilan=usia_kehamilan, paritas=paritas, kader=kader
            )
            for i, skor in enumerate(scores):
                if skor >= 30:
                    kat = 'tinggi'
                elif skor >= 15:
                    kat = 'sedang'
                else:
                    kat = 'rendah'
                days_ago = (len(scores) - 1 - i) * 30
                h = SkriningHasil(
                    ibu=profil, skor=skor, kategori_risiko=kat,
                    jawaban={f'q{j}': min(4, skor // 4) for j in range(4)},
                )
                h.save()
                SkriningHasil.objects.filter(pk=h.pk).update(
                    created_at=timezone.now() - timedelta(days=days_ago)
                )
            # Siaga checklist random
            for item_idx in range(5):
                if random.random() > 0.4:
                    SiagaChecklist.objects.create(
                        ibu=profil, nomor_item=item_idx, sudah_dicentang=True
                    )
            all_ibu_created += 1

        # Distribusi ibu antar kader (tidak rata)
        kader_distribution = [8, 7, 5, 5, 5]  # total ~30

        # Buat preset ibu
        for d in preset_ibu:
            kader = kader_profils[d['kader_idx']]
            make_ibu(d['username'], d['nama_lengkap'], d['usia'],
                     d['usia_kehamilan'], d['paritas'], kader, d['scores'])

        # Buat ibu acak berdasarkan distribusi
        nama_iter = iter(nama_remaining)
        idx = 0
        for kader_idx, jumlah in enumerate(kader_distribution):
            kader = kader_profils[kader_idx]
            # Beberapa slot sudah diisi preset
            preset_count = sum(1 for d in preset_ibu if d['kader_idx'] == kader_idx)
            sisa = jumlah - preset_count
            for _ in range(sisa):
                try:
                    nama = next(nama_iter)
                except StopIteration:
                    break
                username = f'ibu{idx + 1}'
                idx += 1
                usia = random.randint(19, 38)
                usia_kehamilan = random.randint(8, 40)
                paritas = random.randint(0, 3)
                # Generate skor berdasarkan profil risiko
                risk_profile = random.choice(['tinggi', 'sedang', 'rendah', 'rendah'])
                if risk_profile == 'tinggi':
                    base = random.randint(28, 44)
                elif risk_profile == 'sedang':
                    base = random.randint(15, 27)
                else:
                    base = random.randint(3, 14)
                n_scores = random.randint(2, 6)
                scores = [max(0, min(55, base + random.randint(-4, 4))) for _ in range(n_scores)]
                make_ibu(username, nama, usia, usia_kehamilan, paritas, kader, scores)

        self.stdout.write(f'  OK {all_ibu_created} ibu hamil dibuat')

        # ── Summary ───────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('OK Seed selesai!'))
        self.stdout.write(f'  Petugas:  {len(petugas_data)} akun')
        self.stdout.write(f'  Kader:    {len(kader_profils)} akun')
        self.stdout.write(f'  Ibu hamil:{all_ibu_created} akun')
        self.stdout.write(f'  Artikel:  {len(ARTICLES) + 1} artikel')
        self.stdout.write(f'  Jadwal:   {total_jadwal} jadwal')
        self.stdout.write('')
        self.stdout.write('Akun utama (password: pass123):')
        self.stdout.write('  citra    — Ibu Hamil (Risiko Tinggi)')
        self.stdout.write('  rina     — Ibu Hamil (Risiko Sedang)')
        self.stdout.write('  lestari  — Ibu Hamil (Risiko Rendah)')
        self.stdout.write('  putri    — Ibu Hamil (Risiko Rendah)')
        self.stdout.write('  anisa    — Kader Posyandu Melati 1')
        self.stdout.write('  kader2   — Kader Posyandu Melati 2')
        self.stdout.write('  sari     — Petugas Puskesmas')
