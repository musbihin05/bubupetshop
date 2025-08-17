import datetime
from celery import shared_task
from django.utils import timezone
from bookinglayanan.models import BookingLayanan, LayananPenitipan

@shared_task
def cancel_pending_bookings():
    """Membatalkan booking yang belum dibayar setelah 6 jam."""
    batas_waktu = timezone.now() - datetime.timedelta(minutes=1) 

    pending_bookings = BookingLayanan.objects.filter(
        status_booking='pending',
        tanggal_booking__lte=batas_waktu,
        bukti_pembayaran__isnull=True
    )

    for booking in pending_bookings:
        booking.status_booking = 'cancelled'
        booking.tanggal_selesai = timezone.now()
        booking.save()

        # Mengembalikan kapasitas penitipan jika layanan adalah 'sitting'
        if booking.tipe_layanan == 'sitting' and booking.booking_penitipan:
            layanan_penitipan = LayananPenitipan.objects.get(pk=booking.booking_penitipan_id)
            layanan_penitipan.kapasitas_penitipan += 1
            layanan_penitipan.save()

        print(f"Booking #{booking.id_booking} dibatalkan otomatis.")

    print(f"Pemeriksaan selesai. {len(pending_bookings)} booking dibatalkan.")