from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import BookingLayanan, Peliharaan, LayananGrooming, LayananPenitipan, LayananKesehatan
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import weasyprint  # pastikan sudah install: pip install weasyprint

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
        'grooming': layanan_grooming,
        'sitting': layanan_penitipan,
        'medical': layanan_kesehatan,
    }
    
    # Ambil parameter dari URL untuk auto-fill
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

        # Mapping layanan
        booking_grooming = None
        booking_penitipan = None
        booking_kesehatan = None
        harga_booking = 0

        if tipe_layanan == 'grooming':
            try:
                booking_grooming = LayananGrooming.objects.get(pk=layanan_id)
                harga_booking = booking_grooming.harga_grooming
            except LayananGrooming.DoesNotExist:
                booking_grooming = None
        elif tipe_layanan == 'sitting':
            try:
                booking_penitipan = LayananPenitipan.objects.get(pk=layanan_id)
                kapasitas = booking_penitipan.kapasitas_penitipan
                if kapasitas <= 0:
                    messages.info(request, 'Kapasitas penitipan tidak tersedia.')
                    return redirect('bookinglayanan:tambah_booking')
                booking_penitipan.kapasitas_penitipan -= 1
                booking_penitipan.save()
                harga_booking = booking_penitipan.harga_penitipan
                # Validasi durasi layanan
                try:
                    durasi_int = int(durasi_layanan) if durasi_layanan else 0
                except ValueError:
                    durasi_int = 0
                harga_booking = booking_penitipan.harga_penitipan * durasi_int
            except LayananPenitipan.DoesNotExist:
                booking_penitipan = None
        elif tipe_layanan == 'medical':
            try:
                booking_kesehatan = LayananKesehatan.objects.get(pk=layanan_id)
                harga_booking = booking_kesehatan.harga_kesehatan
            except LayananKesehatan.DoesNotExist:
                booking_kesehatan = None

        # Simpan booking
        BookingLayanan.objects.create(
            id_user=user,
            id_hewan=Peliharaan.objects.get(pk=id_hewan),
            tipe_layanan=tipe_layanan,
            harga_booking=harga_booking,
            booking_grooming=booking_grooming,
            booking_penitipan=booking_penitipan,
            booking_kesehatan=booking_kesehatan,
            tanggal_booking=tanggal_booking,
            durasi_layanan=durasi_layanan,
            catatan_booking=catatan_booking
        )
        id_booking = BookingLayanan.objects.latest('id_booking').id_booking
        messages.success(request, 'Booking berhasil dibuat.')
        return redirect('bookinglayanan:detail_pembayaran', booking_id=id_booking)

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

@csrf_exempt
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

