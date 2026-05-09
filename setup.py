"""
Setup script untuk PRENAMENT Django App
Jalankan: python setup.py
"""

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prenament.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from ibu.models import IbuProfil, SkriningHasil
from kader.models import KaderProfil, Jadwal
from petugas.models import PetugasProfil
from datetime import datetime, timedelta

User = get_user_model()

def create_dummy_data():
    """Buat data dummy untuk testing"""
    print("🔧 Membuat data dummy...")
    
    # Hapus user lama jika ada
    User.objects.filter(username__in=['citra', 'rina', 'lestari', 'putri', 'anisa', 'sari']).delete()
    
    # 1. Buat Ibu Hamil
    ibu_data = [
        {'username': 'citra', 'email': 'citra@test.com', 'nama_lengkap': 'Citra Dewi', 'usia': 28, 'usia_kehamilan': 32, 'paritas': 1},
        {'username': 'rina', 'email': 'rina@test.com', 'nama_lengkap': 'Rina Wulandari', 'usia': 26, 'usia_kehamilan': 28, 'paritas': 0},
        {'username': 'lestari', 'email': 'lestari@test.com', 'nama_lengkap': 'Lestari Indah', 'usia': 30, 'usia_kehamilan': 24, 'paritas': 2},
        {'username': 'putri', 'email': 'putri@test.com', 'nama_lengkap': 'Putri Amelia', 'usia': 25, 'usia_kehamilan': 20, 'paritas': 0},
    ]
    
    kader_user = User.objects.create_user(
        username='anisa',
        email='anisa@test.com',
        password='pass123',
        role='kader',
        nama_lengkap='Bidan Anisa'
    )
    
    # Buat Kader Profil
    kader_profil = KaderProfil.objects.create(
        user=kader_user,
        posyandu='Posyandu Melati 1',
        wilayah='Kelurahan Lansot'
    )
    
    for ibu in ibu_data:
        user = User.objects.create_user(
            username=ibu['username'],
            email=ibu['email'],
            password='pass123',
            role='ibu',
            nama_lengkap=ibu['nama_lengkap']
        )
        
        ibu_profil = IbuProfil.objects.create(
            user=user,
            usia=ibu['usia'],
            usia_kehamilan=ibu['usia_kehamilan'],
            paritas=ibu['paritas'],
            kader=kader_profil
        )
        
        # Tambah skrining hasil
        skor = [37, 22, 12, 14][ibu_data.index(ibu)]
        if skor >= 30:
            kategori = 'tinggi'
        elif skor >= 15:
            kategori = 'sedang'
        else:
            kategori = 'rendah'
        
        SkriningHasil.objects.create(
            ibu=ibu_profil,
            skor=skor,
            kategori_risiko=kategori,
            jawaban={'q1': str(skor//4), 'q2': str(skor//5), 'q3': str(skor//6), 'q4': str(skor//7)}
        )
    
    # 2. Buat Petugas
    petugas_user = User.objects.create_user(
        username='sari',
        email='sari@test.com',
        password='pass123',
        role='petugas',
        nama_lengkap='dr. Sari Putri'
    )
    
    PetugasProfil.objects.create(
        user=petugas_user,
        nip='123456789',
        puskesmas='Puskesmas Lansot',
        jabatan='Dokter'
    )
    
    print("✅ Data dummy berhasil dibuat!")
    print("Akun test:")
    print("  Ibu: citra/pass123")
    print("  Kader: anisa/pass123")
    print("  Petugas: sari/pass123")

if __name__ == '__main__':
    # Jalankan migrasi
    print("📦 Menjalankan migrasi database...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Buat data dummy
    create_dummy_data()
    
    print("\n🎉 Setup selesai! Jalankan: python manage.py runserver")
