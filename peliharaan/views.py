from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Peliharaan
from django.conf import settings
import os

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect('user:login')

    user = request.user
    peliharaan = Peliharaan.objects.filter(id_user=user)
    jenis_hewan_choices = Peliharaan.JENIS_HEWAN_CHOICES
    jenis_hewan_dict = {key: value for key, value in jenis_hewan_choices}
   

    # Handle tambah/edit/hapus
    if request.method == 'POST':
        # Tambah/Edit
        if 'nama_hewan' in request.POST:
            id_hewan = request.POST.get('id_hewan')
            nama_hewan = request.POST.get('nama_hewan')
            jenis_hewan = request.POST.get('jenis_hewan')
            umur_hewan = request.POST.get('umur_hewan')
            berat_hewan = request.POST.get('berat_hewan')
            keterangan = request.POST.get('keterangan')
            foto_peliharaan = request.FILES.get('foto_peliharaan')

            if id_hewan:  # Edit
                p = Peliharaan.objects.get(id_hewan=id_hewan, id_user=user)
                # Hapus foto lama jika upload baru
                if foto_peliharaan and p.foto_peliharaan:
                    old_path = p.foto_peliharaan.path
                    if os.path.isfile(old_path):
                        os.remove(old_path)
                p.nama_hewan = nama_hewan
                p.jenis_hewan = jenis_hewan
                p.umur_hewan = umur_hewan
                p.berat_hewan = berat_hewan
                p.keterangan = keterangan
                if foto_peliharaan:
                    p.foto_peliharaan = foto_peliharaan
                p.save()
                messages.success(request, 'Data peliharaan berhasil diperbarui.')
            else:  # Tambah
                Peliharaan.objects.create(
                    id_user=user,
                    nama_hewan=nama_hewan,
                    jenis_hewan=jenis_hewan,
                    umur_hewan=umur_hewan,
                    berat_hewan=berat_hewan,
                    keterangan=keterangan,
                    foto_peliharaan=foto_peliharaan
                )
                messages.success(request, 'Data peliharaan berhasil ditambahkan.')
            return redirect('peliharaan:index')

        # Hapus
        if 'id_hewan' in request.POST and not 'nama_hewan' in request.POST:
            id_hewan = request.POST.get('id_hewan')
            p = Peliharaan.objects.get(id_hewan=id_hewan, id_user=user)
            # Hapus foto
            if p.foto_peliharaan:
                foto_path = p.foto_peliharaan.path
                if os.path.isfile(foto_path):
                    os.remove(foto_path)
            p.delete()
            messages.success(request, 'Data peliharaan berhasil dihapus.')
            return redirect('peliharaan:index')

    context = {
        'title': "Peliharaan",
        'akun': user,
        'peliharaan': peliharaan,
        'jenis_hewan': jenis_hewan_dict,
    }
    return render(request, 'peliharaan/index.html', context)