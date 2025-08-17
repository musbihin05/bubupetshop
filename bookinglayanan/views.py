from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import BookingLayanan, Peliharaan, LayananGrooming, LayananPenitipan, LayananKesehatan,DailyCapacity
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import weasyprint  # pastikan sudah install: pip install weasyprint
from datetime import datetime, timedelta
import json

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect('user:login')

    user = request.user
    bookings = BookingLayanan.objects.filter(id_user=user).order_by('-id_booking')
    # bookings = []
   
    # return HttpResponse(bookings)
    status_choices = BookingLayanan.STATUS_CHOICES
    status_dict = {key: value for key, value in status_choices}

    # Perbaiki upload bukti pembayaran agar update gambar dan catatan
    if request.method == 'POST' and 'upload_bukti' in request.POST:
        booking_id = request.POST.get('booking_id')
        bukti_file = request.FILES.get('bukti_pembayaran')
        catatan = request.POST.get('catatan_bayar', '')
        booking = get_object_or_404(BookingLayanan, id_booking=booking_id, id_user=request.user)
        # Hapus gambar lama jika ada dan upload baru
        if bukti_file:
            if booking.bukti_pembayaran:
                try:
                    old_path = booking.bukti_pembayaran.path
                    import os
                    if os.path.isfile(old_path):
                        os.remove(old_path)
                except Exception:
                    pass
            booking.bukti_pembayaran = bukti_file
        # Update catatan pelanggan
        if catatan:
            booking.catatan_booking = catatan
        booking.save()
        messages.success(request, 'Bukti pembayaran berhasil diupload.')
        return redirect('bookinglayanan:index')

    context = {
        'title': "Booking Layanan",
        'akun': user,
        'status': status_dict,
        'bookings': bookings
    }
    return render(request, 'booking/index.html', context)



def tambah_booking(request):
    if not request.user.is_authenticated:
        return redirect('user:login')

    user = request.user
    tipe_layanan_choices = BookingLayanan.JENIS_LAYANAN_CHOICES
    tipe_layanan_dict = {key: value for key, value in tipe_layanan_choices}
    layanan_grooming = LayananGrooming.objects.all()
    layanan_penitipan = LayananPenitipan.objects.all()
    layanan_kesehatan = LayananKesehatan.objects.all()
    layanan = {
        'grooming': [
            {
                'id': item.id_grooming,
                'nama_layanan': item.nama_grooming,
                'harga': float(item.harga_grooming)
            } for item in layanan_grooming
        ],
        'sitting': [
            {
                'id': item.id_penitipan,
                'nama_layanan': item.jenis_penitipan,
                'harga': float(item.harga_penitipan)
            } for item in layanan_penitipan
        ],
        'medical': [
            {
                'id': item.id_kesehatan,
                'nama_layanan': item.nama_kesehatan,
                'harga': float(item.harga_kesehatan)
            } for item in layanan_kesehatan
        ],
    }

    tipe_param = request.GET.get('tipe')
    id_param = request.GET.get('id')
    peliharaan = Peliharaan.objects.filter(id_user=user)

    if request.method == 'POST':
        id_hewan = request.POST.get('id_hewan')
        tipe_layanan_str = request.POST.get('tipe_layanan')
        layanan_id = request.POST.get('layanan')
        tanggal_booking_str = request.POST.get('tanggal')
        durasi = request.POST.get('durasi')
        catatan = request.POST.get('catatan')
        bukti_pembayaran_file = request.FILES.get('bukti_pembayaran')

        if not id_hewan or not tipe_layanan_str or not layanan_id or not tanggal_booking_str:
            messages.error(request, "Semua kolom dengan tanda (*) wajib diisi.")
            return redirect('bookinglayanan:tambah_booking')

        tanggal_booking_obj = datetime.strptime(tanggal_booking_str, '%Y-%m-%d %H:%M').date()
        tanggal_selesai = tanggal_booking_obj + timedelta(days=int(durasi)) if durasi else None
        
        harga_booking = 0
        booking_penitipan_obj = None
        booking_grooming_obj = None
        booking_kesehatan_obj = None

        if tipe_layanan_str == 'sitting':
            try:
                booking_penitipan_obj = LayananPenitipan.objects.get(pk=layanan_id)
                harga_booking = booking_penitipan_obj.harga_penitipan * int(durasi)
                kapasitas_cukup = True
                
                for i in range(int(durasi)):
                    tanggal_per_hari = tanggal_booking_obj + timedelta(days=i)
                    
                    kapasitas_harian, created = DailyCapacity.objects.get_or_create(
                        layanan_penitipan=booking_penitipan_obj,
                        tanggal=tanggal_per_hari,
                        defaults={'kapasitas_tersedia': booking_penitipan_obj.kapasitas_penitipan}
                    )
                    
                    if kapasitas_harian.kapasitas_tersedia <= 0:
                        kapasitas_cukup = False
                        break

            except LayananPenitipan.DoesNotExist:
                messages.error(request, 'Layanan penitipan tidak ditemukan.')
                return redirect('bookinglayanan:tambah_booking')

            if not kapasitas_cukup:
                messages.error(request, 'Maaf, kapasitas tidak tersedia pada salah satu tanggal yang Anda pilih.')
                return redirect('bookinglayanan:tambah_booking')
            
            for i in range(int(durasi)):
                tanggal_per_hari = tanggal_booking_obj + timedelta(days=i)
                kapasitas_harian = DailyCapacity.objects.get(
                    layanan_penitipan=booking_penitipan_obj,
                    tanggal=tanggal_per_hari
                )
                kapasitas_harian.kapasitas_tersedia -= 1
                kapasitas_harian.save()

        elif tipe_layanan_str == 'grooming':
            try:
                booking_grooming_obj = LayananGrooming.objects.get(pk=layanan_id)
                harga_booking = booking_grooming_obj.harga_grooming
            except LayananGrooming.DoesNotExist:
                messages.error(request, 'Layanan jasa tidak ditemukan.')
                return redirect('bookinglayanan:tambah_booking')
        
        elif tipe_layanan_str == 'medical':
            try:
                booking_kesehatan_obj = LayananKesehatan.objects.get(pk=layanan_id)
                harga_booking = booking_kesehatan_obj.harga_kesehatan
            except LayananKesehatan.DoesNotExist:
                messages.error(request, 'Layanan jasa tidak ditemukan.')
                return redirect('bookinglayanan:tambah_booking')

        booking_obj = BookingLayanan.objects.create(
            id_user=request.user,
            id_hewan=Peliharaan.objects.get(pk=id_hewan),
            tipe_layanan=tipe_layanan_str,
            booking_penitipan=booking_penitipan_obj,
            booking_grooming=booking_grooming_obj,
            booking_kesehatan=booking_kesehatan_obj,
            harga_booking=harga_booking,
            tanggal_booking=tanggal_booking_obj,
            tanggal_selesai=tanggal_selesai,
            durasi_layanan=durasi,
            catatan_booking=catatan
        )
        messages.success(request, 'Booking berhasil!')
        return redirect('bookinglayanan:detail_pembayaran', booking_id=booking_obj.id_booking)

    context = {
      'title': "Buat Booking",
      'akun': user,
      'peliharaan': peliharaan,
      'tipe_layanan': tipe_layanan_dict,
      'layanan': {
        'grooming': [
          {
            'id': item.id_grooming,
            'nama_layanan': item.nama_grooming,
            'harga': float(item.harga_grooming)
          } for item in layanan_grooming
        ],
        'sitting': [
          {
            'id': item.id_penitipan,
            'nama_layanan': item.jenis_penitipan,
            'harga': float(item.harga_penitipan)
          } for item in layanan_penitipan
        ],
        'medical': [
          {
            'id': item.id_kesehatan,
            'nama_layanan': item.nama_kesehatan,
            'harga': float(item.harga_kesehatan)
          } for item in layanan_kesehatan
        ],
      },
      'auto_tipe': tipe_param,
      'auto_id': id_param,
    }
    return render(request, 'booking/booking.html', context)


def get_daily_capacity(request):
    if request.method == 'GET':
        tanggal_str = request.GET.get('tanggal')
        layanan_id = request.GET.get('layanan_id')
        durasi_str = request.GET.get('durasi')
        bulan_view = request.GET.get('bulan')
        
        if not tanggal_str or not layanan_id:
            return JsonResponse({'error': 'Data yang dibutuhkan tidak lengkap.'}, status=400)
        
        try:
            if bulan_view:
                # PERBAIKAN: Format string untuk parse tanggal yang tanpa jam
                tanggal_mulai = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
                layanan_penitipan_obj = LayananPenitipan.objects.get(pk=layanan_id)

                first_day_of_month = tanggal_mulai.replace(day=1)
                
                # Perhitungan last day of month yang lebih aman
                if first_day_of_month.month == 12:
                    last_day_of_month = first_day_of_month.replace(year=first_day_of_month.year + 1, month=1) - timedelta(days=1)
                else:
                    last_day_of_month = first_day_of_month.replace(month=first_day_of_month.month + 1) - timedelta(days=1)

                kapasitas_bulan = {}
                current_day = first_day_of_month
                while current_day <= last_day_of_month:
                    kapasitas_harian, created = DailyCapacity.objects.get_or_create(
                        layanan_penitipan=layanan_penitipan_obj,
                        tanggal=current_day,
                        defaults={'kapasitas_tersedia': layanan_penitipan_obj.kapasitas_penitipan}
                    )
                    kapasitas_bulan[current_day.strftime('%Y-%m-%d')] = kapasitas_harian.kapasitas_tersedia
                    current_day += timedelta(days=1)
                
                return JsonResponse({'kapasitas_bulan': kapasitas_bulan})

            # Jika permintaan adalah untuk validasi booking dengan durasi
            durasi = int(durasi_str)
            if durasi <= 0:
                return JsonResponse({
                    'kapasitas_cukup': False,
                    'pesan': 'Durasi booking harus lebih dari 0 hari.'
                })
            
            # PERBAIKAN: Format string untuk parse tanggal yang dengan jam
            tanggal_mulai = datetime.strptime(tanggal_str, '%Y-%m-%d %H:%M').date()
            layanan_penitipan_obj = LayananPenitipan.objects.get(pk=layanan_id)

            kapasitas_minimum_tersedia = float('inf')
            
            for i in range(durasi):
                tanggal_per_hari = tanggal_mulai + timedelta(days=i)
                
                kapasitas_harian, created = DailyCapacity.objects.get_or_create(
                    layanan_penitipan=layanan_penitipan_obj,
                    tanggal=tanggal_per_hari,
                    defaults={'kapasitas_tersedia': layanan_penitipan_obj.kapasitas_penitipan}
                )
                
                if kapasitas_harian.kapasitas_tersedia <= 0:
                    return JsonResponse({
                        'kapasitas_cukup': False,
                        'pesan': f'Maaf, kapasitas tidak tersedia di tanggal {tanggal_per_hari.strftime("%d %B %Y")}.'
                    })
                
                kapasitas_minimum_tersedia = min(kapasitas_minimum_tersedia, kapasitas_harian.kapasitas_tersedia)

            return JsonResponse({
                'kapasitas_cukup': True,
                'kapasitas_tersedia': kapasitas_minimum_tersedia
            })
        
        except (ValueError, LayananPenitipan.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Metode request tidak diizinkan.'}, status=405)


def detail_booking(request, booking_id):
    booking = get_object_or_404(BookingLayanan, id_booking=booking_id, id_user=request.user)
    data = {
        'id_booking': booking.id_booking,
        'tanggal_booking': booking.tanggal_booking.strftime('%d %b %Y %H:%M') if booking.tanggal_booking else '',
        'tanggal_selesai': booking.tanggal_selesai.strftime('%d %b %Y %H:%M') if booking.tanggal_selesai else '',
        'durasi_layanan': booking.durasi_layanan,
        'status_booking': booking.status_booking,
        'catatan_booking': booking.catatan_booking,
        'harga_booking': float(booking.harga_booking),
        'bukti_pembayaran': booking.bukti_pembayaran.url if booking.bukti_pembayaran else '',
        'hewan': {
            'nama': booking.id_hewan.nama_hewan,
            'jenis': booking.id_hewan.jenis_hewan,
            'berat': float(booking.id_hewan.berat_hewan),
        },
        'layanan': '',
    }
    if booking.tipe_layanan == 'grooming' and booking.booking_grooming:
        data['layanan'] = booking.booking_grooming.nama_grooming
    elif booking.tipe_layanan == 'sitting' and booking.booking_penitipan:
        data['layanan'] = booking.booking_penitipan.jenis_penitipan
    elif booking.tipe_layanan == 'medical' and booking.booking_kesehatan:
        data['layanan'] = booking.booking_kesehatan.nama_kesehatan
    else:
        data['layanan'] = booking.tipe_layanan
    return JsonResponse(data)

def detail_pembayaran(request, booking_id):
    booking = get_object_or_404(BookingLayanan, id_booking=booking_id, id_user=request.user)
    jenis_layanan = BookingLayanan.JENIS_LAYANAN_CHOICES
    layanan_dict = {key: value for key, value in jenis_layanan}
    layanan = ''
    
    if booking.tipe_layanan == 'grooming' and booking.booking_grooming:
        layanan = booking.booking_grooming.nama_grooming
    elif booking.tipe_layanan == 'sitting' and booking.booking_penitipan:
        layanan = booking.booking_penitipan.jenis_penitipan
    elif booking.tipe_layanan == 'medical' and booking.booking_kesehatan:
        layanan = booking.booking_kesehatan.nama_kesehatan

   
    context = {
        "title": "Detail Pembayaran BK-{}".format(booking.id_booking),
        "totalBayar": float(booking.harga_booking),
        "booking": {
          "id_booking": booking.id_booking,
          "jenis_layanan": layanan_dict.get(booking.tipe_layanan, 'Unknown'),
          "layanan": layanan,
        }
    }
    
    
    return render(request, 'booking/pembayaran.html', context)

