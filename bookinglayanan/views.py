from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import BookingLayanan, Peliharaan, LayananGrooming, LayananPenitipan, LayananKesehatan,DailyCapacity
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import weasyprint  # pastikan sudah install: pip install weasyprint
from datetime import datetime, timedelta
import json
import os


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect('user:login')

    user = request.user
    bookings = BookingLayanan.objects.filter(id_user=user).order_by('-id_booking')
    
    status_choices = BookingLayanan.STATUS_CHOICES
    status_dict = {key: value for key, value in status_choices}

    if request.method == 'POST' and 'upload_bukti' in request.POST:
        booking_id = request.POST.get('booking_id')
        bukti_file = request.FILES.get('bukti_pembayaran')
        catatan = request.POST.get('catatan_bayar', '')
        booking = get_object_or_404(BookingLayanan, id_booking=booking_id, id_user=request.user)
        
        if bukti_file:
            if booking.bukti_pembayaran:
                try:
                    old_path = booking.bukti_pembayaran.path
                    if os.path.isfile(old_path):
                        os.remove(old_path)
                except Exception:
                    pass
            booking.bukti_pembayaran = bukti_file
        
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
        tipe_layanan = request.POST.get('tipe_layanan')
        layanan_id = request.POST.get('layanan')
        tanggal_booking = request.POST.get('tanggal')
        durasi_layanan = request.POST.get('durasi')
        catatan_booking = request.POST.get('catatan')

        if not id_hewan or not tipe_layanan or not layanan_id or not tanggal_booking:
            messages.error(request, "Semua kolom dengan tanda (*) wajib diisi.")
            return redirect('bookinglayanan:tambah_booking')

        tanggal_booking_obj = datetime.strptime(tanggal_booking, '%Y-%m-%d %H:%M').date()
        tanggal_selesai = tanggal_booking_obj + timedelta(days=int(durasi_layanan)) if durasi_layanan else None
        
        harga_booking = 0
        booking_penitipan = None
        booking_grooming = None
        booking_kesehatan = None

        if tipe_layanan == 'sitting':
            try:
                booking_penitipan = LayananPenitipan.objects.get(pk=layanan_id)
                harga_booking = booking_penitipan.harga_penitipan * int(durasi_layanan)
                kapasitas_cukup = True
                
                for i in range(int(durasi_layanan)):
                    tanggal_per_hari = tanggal_booking_obj + timedelta(days=i)
                    
                    kapasitas_harian, created = DailyCapacity.objects.get_or_create(
                        layanan_penitipan=booking_penitipan,
                        tanggal=tanggal_per_hari,
                        defaults={'kapasitas_tersedia': booking_penitipan.kapasitas_penitipan}
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
            
            for i in range(int(durasi_layanan)):
                tanggal_per_hari = tanggal_booking_obj + timedelta(days=i)
                kapasitas_harian = DailyCapacity.objects.get(
                    layanan_penitipan=booking_penitipan,
                    tanggal=tanggal_per_hari
                )
                kapasitas_harian.kapasitas_tersedia -= 1
                kapasitas_harian.save()

        elif tipe_layanan == 'grooming':
            try:
                booking_grooming = LayananGrooming.objects.get(pk=layanan_id)
                harga_booking = booking_grooming.harga_grooming
            except LayananGrooming.DoesNotExist:
                messages.error(request, 'Layanan jasa tidak ditemukan.')
                return redirect('bookinglayanan:tambah_booking')
        
        elif tipe_layanan == 'medical':
            try:
                booking_kesehatan = LayananKesehatan.objects.get(pk=layanan_id)
                harga_booking = booking_kesehatan.harga_kesehatan
            except LayananKesehatan.DoesNotExist:
                messages.error(request, 'Layanan jasa tidak ditemukan.')
                return redirect('bookinglayanan:tambah_booking')

        booking_obj = BookingLayanan.objects.create(
            id_user=user,
            id_hewan=Peliharaan.objects.get(pk=id_hewan),
            tipe_layanan=tipe_layanan,
            booking_penitipan=booking_penitipan,
            booking_grooming=booking_grooming,
            booking_kesehatan=booking_kesehatan,
            harga_booking=harga_booking,
            tanggal_booking=tanggal_booking,
            tanggal_selesai=tanggal_selesai,
            durasi_layanan=durasi_layanan,
            catatan_booking=catatan_booking
        )
        messages.success(request, 'Booking berhasil!')
        return redirect('bookinglayanan:detail_pembayaran', booking_id=booking_obj.id_booking)

    context = {
      'title': "Buat Booking",
      'akun': user,
      'peliharaan': peliharaan,
      'tipe_layanan': tipe_layanan_dict,
      'layanan': layanan,
      'auto_tipe': tipe_param,
      'auto_id': id_param,
    }
    return render(request, 'booking/booking.html', context)


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

def get_daily_capacity(request):
    if request.method == 'GET':
        tanggal_str = request.GET.get('tanggal')
        layanan_id = request.GET.get('layanan_id')
        durasi_str = request.GET.get('durasi')
        bulan_view = request.GET.get('bulan')
        
        if not tanggal_str or not layanan_id:
            return JsonResponse({'error': 'Data yang dibutuhkan tidak lengkap.'}, status=400)
        
        try:
            layanan_penitipan_obj = LayananPenitipan.objects.get(pk=layanan_id)

            if bulan_view:
                tanggal_mulai_bulan = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
                first_day_of_month = tanggal_mulai_bulan.replace(day=1)
                
                # Menginisialisasi kapasitas untuk setiap hari dalam sebulan
                kapasitas_bulan = {}
                today = date.today()
                
                current_day = first_day_of_month
                while current_day.month == first_day_of_month.month:
                    # Pastikan hanya hari di masa depan dan hari kerja yang ditampilkan
                    if current_day >= today and current_day.weekday() < 5:  # 0=Senin, 4=Jumat
                        kapasitas_bulan[current_day.strftime('%Y-%m-%d')] = layanan_penitipan_obj.kapasitas_penitipan
                    current_day += timedelta(days=1)
                
                # Mengambil data kapasitas dari database dan menimpa nilai default
                kapasitas_harian_queryset = DailyCapacity.objects.filter(
                    layanan_penitipan=layanan_penitipan_obj,
                    tanggal__gte=first_day_of_month,
                    tanggal__lte=current_day - timedelta(days=1)
                )
                
                for item in kapasitas_harian_queryset:
                    kapasitas_bulan[item.tanggal.strftime('%Y-%m-%d')] = item.kapasitas_tersedia
                
                return JsonResponse({'kapasitas_bulan': kapasitas_bulan})

            durasi = int(durasi_str)
            if durasi <= 0:
                return JsonResponse({
                    'kapasitas_cukup': False,
                    'pesan': 'Durasi booking harus lebih dari 0 hari.'
                })
            
            tanggal_mulai = datetime.strptime(tanggal_str, '%Y-%m-%d %H:%M').date()
            
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
                        'pesan': f'Maaf, slot penitipan kosong pada tanggal {tanggal_per_hari.strftime("%d %B %Y")}.'
                    })
                
                kapasitas_minimum_tersedia = min(kapasitas_minimum_tersedia, kapasitas_harian.kapasitas_tersedia)

            return JsonResponse({
                'kapasitas_cukup': True,
                'kapasitas_tersedia': kapasitas_minimum_tersedia
            })
        
        except (ValueError, LayananPenitipan.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Metode request tidak diizinkan.'}, status=405)


    """
    Mengambil data kapasitas harian untuk tampilan kalender bulanan.
    """
    try:
        tanggal_mulai_bulan = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        year, month = tanggal_mulai_bulan.year, tanggal_mulai_bulan.month
        kapasitas_bulan = {}

        # Ambil data dari tabel DailyCapacity saja
        kapasitas_harian_queryset = DailyCapacity.objects.filter(
            layanan_penitipan=layanan_penitipan_obj,
            tanggal__year=year,
            tanggal__month=month
        )
        for item in kapasitas_harian_queryset:
            kapasitas_bulan[item.tanggal.strftime('%Y-%m-%d')] = item.kapasitas_tersedia

        return JsonResponse({
            'mode': 'bulan',
            'data': kapasitas_bulan
        })
    except Exception as e:
        return JsonResponse({'error': f'Terjadi kesalahan saat memuat data bulanan: {e}'}, status=500)


    if request.method not in ['GET', 'POST']:
        return JsonResponse({'error': 'Metode request tidak diizinkan.'}, status=405)

    # --- Ambil data dari GET atau POST JSON ---
    if request.method == 'GET':
        tanggal_str = request.GET.get('tanggal')
        layanan_id_str = request.GET.get('layanan_id')
        durasi_str = request.GET.get('durasi')
        bulan_view = request.GET.get('bulan')
    else:  # POST JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON tidak valid.'}, status=400)
        tanggal_str = data.get('tanggal')
        layanan_id_str = data.get('layanan_id')
        durasi_str = data.get('durasi')
        bulan_view = data.get('bulan')

    # --- Validasi awal input ---
    if not tanggal_str or not layanan_id_str:
        return JsonResponse({'error': 'Data yang dibutuhkan tidak lengkap.'}, status=400)

    try:
        layanan_id = int(layanan_id_str)
        layanan_penitipan_obj = LayananPenitipan.objects.get(pk=layanan_id)

        # --- Panggil fungsi yang sesuai berdasarkan mode permintaan ---
        if bulan_view:
            return get_monthly_capacity(request, layanan_penitipan_obj, tanggal_str)

        # --- Mode Pengecekan Durasi Booking ---
        if not durasi_str:
            return JsonResponse({'error': 'Durasi booking dibutuhkan.'}, status=400)

        durasi = int(durasi_str)
        if durasi <= 0:
            return JsonResponse({'mode': 'durasi', 'data': {
                'kapasitas_cukup': False,
                'pesan': 'Durasi booking harus lebih dari 0 hari.'
            }})

        tanggal_mulai = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        kapasitas_minimum_tersedia = float('inf')

        for i in range(durasi):
            tanggal_per_hari = tanggal_mulai + timedelta(days=i)
            kapasitas_harian, _ = DailyCapacity.objects.get_or_create(
                layanan_penitipan=layanan_penitipan_obj,
                tanggal=tanggal_per_hari,
                defaults={'kapasitas_tersedia': layanan_penitipan_obj.kapasitas_penitipan}
            )
            if kapasitas_harian.kapasitas_tersedia <= 0:
                return JsonResponse({'mode': 'durasi', 'data': {
                    'kapasitas_cukup': False,
                    'pesan': f'Maaf, kapasitas tidak tersedia di tanggal {tanggal_per_hari.strftime("%d %B %Y")}.'
                }})

            kapasitas_minimum_tersedia = min(kapasitas_minimum_tersedia, kapasitas_harian.kapasitas_tersedia)

        return JsonResponse({'mode': 'durasi', 'data': {
            'kapasitas_cukup': True,
            'kapasitas_tersedia': kapasitas_minimum_tersedia
        }})

    except (ValueError, LayananPenitipan.DoesNotExist) as e:
        return JsonResponse({'error': f'Layanan Penitipan tidak ditemukan atau ID tidak valid: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Terjadi kesalahan server: {e}'}, status=500)