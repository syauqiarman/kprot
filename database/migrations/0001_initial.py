# Generated by Django 5.1.7 on 2025-03-12 09:25

import database.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramMBKM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('minimum_sks', models.IntegerField()),
                ('maksimum_sks', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=16, unique=True)),
                ('gasal_genap', models.CharField(max_length=5)),
                ('tahun', models.IntegerField()),
                ('aktif', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Dosen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Kaprodi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ManajemenFakultas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PembimbingAkademik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mahasiswa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('npm', models.CharField(max_length=20, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('pa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.pembimbingakademik')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Penyelia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True, validators=[database.validators.validate_email_penyelia])),
                ('perusahaan', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PendaftaranMBKM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah_semester', models.IntegerField(validators=[database.validators.validate_jumlah_semester_mbkm])),
                ('sks_diambil', models.IntegerField(blank=True, null=True, validators=[database.validators.validate_sks_diambil])),
                ('request_status_merdeka', models.BooleanField(default=False)),
                ('rencana_lulus_semester_ini', models.BooleanField(default=False)),
                ('role', models.CharField(blank=True, max_length=255, null=True)),
                ('estimasi_sks_konversi', models.IntegerField(blank=True, null=True)),
                ('persetujuan_pa', models.FileField(blank=True, null=True, upload_to='persetujuan_pa/')),
                ('tanggal_persetujuan', models.DateField(blank=True, null=True)),
                ('tanggal_mulai', models.DateField(blank=True, null=True)),
                ('tanggal_selesai', models.DateField(blank=True, null=True)),
                ('pernyataan_komitmen', models.BooleanField(default=False, validators=[database.validators.validate_pernyataan_komitmen])),
                ('status_pendaftaran', models.CharField(choices=[('Menunggu Persetujuan PA', 'Menunggu Persetujuan PA'), ('Ditolak PA', 'Ditolak PA'), ('Menunggu Persetujuan Kaprodi', 'Menunggu Persetujuan Kaprodi'), ('Ditolak Kaprodi', 'Ditolak Kaprodi'), ('Menunggu Verifikasi Dosen', 'Menunggu Verifikasi Dosen'), ('Ditolak Dosen', 'Ditolak Dosen'), ('Menunggu Detil', 'Menunggu Detil'), ('Terdaftar', 'Terdaftar')], default='Menunggu Persetujuan PA', max_length=50)),
                ('feedback_penolakan', models.TextField(blank=True, null=True)),
                ('history', models.JSONField()),
                ('file_timestamp', models.DateTimeField(blank=True, null=True)),
                ('mahasiswa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.mahasiswa')),
                ('penyelia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.penyelia')),
                ('program_mbkm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.programmbkm')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.semester')),
            ],
        ),
        migrations.CreateModel(
            name='PendaftaranKP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah_semester', models.IntegerField(validators=[database.validators.validate_jumlah_semester_kp])),
                ('sks_lulus', models.IntegerField(validators=[database.validators.validate_sks_lulus])),
                ('role', models.CharField(blank=True, max_length=255, null=True)),
                ('total_jam_kerja', models.IntegerField(blank=True, null=True, validators=[database.validators.validate_total_jam_kerja])),
                ('tanggal_mulai', models.DateField(blank=True, null=True)),
                ('tanggal_selesai', models.DateField(blank=True, null=True)),
                ('pernyataan_komitmen', models.BooleanField(default=False, validators=[database.validators.validate_pernyataan_komitmen])),
                ('status_pendaftaran', models.CharField(choices=[('Menunggu Detil', 'Menunggu Detil'), ('Terdaftar', 'Terdaftar')], default='Menunggu Detil', max_length=50)),
                ('history', models.JSONField()),
                ('mahasiswa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.mahasiswa')),
                ('penyelia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.penyelia')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.semester')),
            ],
        ),
    ]
