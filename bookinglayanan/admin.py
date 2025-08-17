from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.admin import DateFieldListFilter
from .models import BookingLayanan, DailyCapacity, LayananPenitipan
from riwayatpenjualan.models import RiwayatPenjualan
from django.urls import reverse
from datetime import timedelta


@admin.register(BookingLayanan)
class BookingLayananAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.is_staff
      
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff
      
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser 
      
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff
      
    list_display = (
        'booking_info', 'user_no_hp', 'tipe_layanan_display', 'status_booking_badge',
        'status_bayar', 'harga_booking_rupiah', 'tanggal_selesai',
    )
    search_fields = ('id_booking', 'id_user__email', 'tipe_layanan')
    
    list_filter = (
        ('tanggal_booking', DateFieldListFilter),
        'status_booking',
        'tipe_layanan',
    )
    ordering = ('-tanggal_booking',)

    actions = ['set_status_konfirmasi', 'set_status_selesai', 'set_status_batal', 'export_as_csv']
    
    def user_no_hp(self, obj):
        if obj.id_user and hasattr(obj.id_user, 'no_hp'):
            url = reverse('admin:user_user_change', args=[obj.id_user.id])
            return format_html('<a href="{}">{}</a>', url, obj.id_user.no_hp)
        return '-'
    user_no_hp.short_description = 'No HP Pelanggan'
    user_no_hp.admin_order_field = 'id_user__no_hp'

    def tipe_layanan_display(self, obj):
        return obj.get_tipe_layanan_display()
    tipe_layanan_display.short_description = 'Tipe Layanan'
    tipe_layanan_display.admin_order_field = 'tipe_layanan'

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=laporan_booking.csv'
        writer = csv.writer(response)
        writer.writerow(['ID Booking', 'User', 'Hewan', 'Layanan', 'Harga', 'Tanggal', 'Status'])
        for obj in queryset:
            writer.writerow([
                obj.id_booking,
                obj.id_user.email if obj.id_user else '',
                obj.id_hewan.nama_hewan if obj.id_hewan else '',
                obj.get_tipe_layanan_display(),
                obj.harga_booking,
                obj.tanggal_booking,
                obj.get_status_booking_display(),
            ])
        return response
    export_as_csv.short_description = "Export Selected to CSV"

    def booking_info(self, obj):
        return format_html(
            '<div><strong>#BK-{}</strong><br><span style="color: #888;">{}</span></div>',
            obj.id_booking,
            obj.tanggal_booking.strftime('%d %b %Y %H:%M') if obj.tanggal_booking else '-'
        )
    booking_info.short_description = 'No. Booking'
    booking_info.admin_order_field = 'id_booking'

    def set_status_selesai(self, request, queryset):
        updated = 0
        added_to_history = 0
        for booking in queryset:
            previous_status = booking.status_booking
            
            if previous_status != 'completed':
                booking.status_booking = 'completed'
                booking.tanggal_selesai = timezone.now()
                
                # Kapasitas tidak perlu dikembalikan saat selesai
                
                booking.save()
                updated += 1
                
                nama_layanan = ""
                if booking.tipe_layanan == 'grooming' and booking.booking_grooming:
                    nama_layanan = f"{booking.booking_grooming.nama_grooming} (Grooming)"
                elif booking.tipe_layanan == 'sitting' and booking.booking_penitipan:
                    nama_layanan = f"{booking.booking_penitipan.jenis_penitipan} (Penitipan)"
                elif booking.tipe_layanan == 'medical' and booking.booking_kesehatan:
                    nama_layanan = f"{booking.booking_kesehatan.nama_kesehatan} (Kesehatan)"
                else:
                    nama_layanan = booking.get_tipe_layanan_display()
                    
                nama_pelanggan = booking.id_user.email
                if hasattr(booking.id_user, 'nama') and booking.id_user.nama:
                    nama_pelanggan = booking.id_user.nama
                    
                no_hp = ""
                if hasattr(booking.id_user, 'no_hp') and booking.id_user.no_hp:
                    no_hp = f" ({booking.id_user.no_hp})"
                    
                if not RiwayatPenjualan.objects.filter(
                    pelanggan=f"{nama_pelanggan}{no_hp}",
                    layanan=nama_layanan,
                    status='completed',
                    total_penjualan=booking.harga_booking
                ).exists():
                    RiwayatPenjualan.objects.create(
                        tanggal_penjualan=timezone.now(),
                        pelanggan=f"{nama_pelanggan}{no_hp}",
                        layanan=nama_layanan,
                        status='completed',
                        total_penjualan=booking.harga_booking
                    )
                    added_to_history += 1
                else:
                    booking.save()
                    updated += 1
                    
        if added_to_history > 0:
            self.message_user(request, f"{updated} booking diubah ke status selesai, {added_to_history} ditambahkan ke riwayat penjualan")
        else:
            self.message_user(request, f"{updated} booking diubah ke status selesai")
    set_status_selesai.short_description = "Ubah status ke Selesai"
    
    def set_status_konfirmasi(self, request, queryset):
        updated = 0
        for booking in queryset:
            booking.status_booking = 'confirmed'
            booking.save()
            updated += 1
        self.message_user(request, f"{updated} booking diubah ke status konfirmasi")
    set_status_konfirmasi.short_description = "Ubah status ke Konfirmasi"
    
    def set_status_batal(self, request, queryset):
        updated = 0
        added_to_history = 0
        for booking in queryset:
            previous_status = booking.status_booking
            
            if previous_status != 'cancelled':
                booking.status_booking = 'cancelled'
                booking.tanggal_selesai = timezone.now()
                
                # Hapus baris ini: layanan_penitipan.kapasitas_penitipan += 1
                if booking.tipe_layanan == 'sitting' and booking.booking_penitipan and booking.tanggal_booking and booking.durasi_layanan:
                    tanggal_mulai = booking.tanggal_booking.date()
                    durasi = booking.durasi_layanan
                    for i in range(durasi):
                        tanggal_per_hari = tanggal_mulai + timedelta(days=i)
                        try:
                            kapasitas_harian = DailyCapacity.objects.get(
                                layanan_penitipan=booking.booking_penitipan,
                                tanggal=tanggal_per_hari
                            )
                            kapasitas_harian.kapasitas_tersedia += 1
                            kapasitas_harian.save()
                        except DailyCapacity.DoesNotExist:
                            pass
                
                booking.save()
                updated += 1
                
                nama_layanan = ""
                if booking.tipe_layanan == 'grooming' and booking.booking_grooming:
                    nama_layanan = f"{booking.booking_grooming.nama_grooming} (Grooming)"
                elif booking.tipe_layanan == 'sitting' and booking.booking_penitipan:
                    nama_layanan = f"{booking.booking_penitipan.jenis_penitipan} (Penitipan)"
                elif booking.tipe_layanan == 'medical' and booking.booking_kesehatan:
                    nama_layanan = f"{booking.booking_kesehatan.nama_kesehatan} (Kesehatan)"
                else:
                    nama_layanan = booking.get_tipe_layanan_display()
                    
                nama_pelanggan = booking.id_user.email
                if hasattr(booking.id_user, 'nama') and booking.id_user.nama:
                    nama_pelanggan = booking.id_user.nama
                    
                no_hp = ""
                if hasattr(booking.id_user, 'no_hp') and booking.id_user.no_hp:
                    no_hp = f" ({booking.id_user.no_hp})"
                    
                if not RiwayatPenjualan.objects.filter(
                    pelanggan=f"{nama_pelanggan}{no_hp}",
                    layanan=nama_layanan,
                    status='cancelled',
                    total_penjualan=booking.harga_booking
                ).exists():
                    RiwayatPenjualan.objects.create(
                        tanggal_penjualan=timezone.now(),
                        pelanggan=f"{nama_pelanggan}{no_hp}",
                        layanan=nama_layanan,
                        status='cancelled',
                        total_penjualan=booking.harga_booking
                    )
                    added_to_history += 1
                else:
                    booking.save()
                    updated += 1
        
        if added_to_history > 0:
            self.message_user(request, f"{updated} booking diubah ke status batal, {added_to_history} ditambahkan ke riwayat penjualan")
        else:
            self.message_user(request, f"{updated} booking diubah ke status batal")
    set_status_batal.short_description = "Ubah status ke Batal"

    def status_booking_badge(self, obj):
        color = {
            'pending': 'warning',
            'confirmed': 'info',
            'completed': 'success',
            'cancelled': 'danger',
        }.get(obj.status_booking, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.status_booking
        )
    status_booking_badge.short_description = 'Status Booking'
    status_booking_badge.admin_order_field = 'status_booking'

    def status_bayar(self, obj):
        if obj.bukti_pembayaran:
            return format_html(
                '<span class="badge badge-success">Sudah Bayar</span><br>'
                '<a href="{}" target="_blank">Lihat Bukti</a>',
                obj.bukti_pembayaran.url
            )
        else:
            return format_html('<span class="badge badge-warning">Belum Bayar</span>')
    status_bayar.short_description = 'Status Bayar'
    status_bayar.admin_order_field = 'bukti_pembayaran'

    def harga_booking_rupiah(self, obj):
        value = int(obj.harga_booking)
        rupiah = f"Rp {value:,}".replace(",", ".")
        return format_html('<span>{}</span>', rupiah)
    harga_booking_rupiah.short_description = 'Harga Booking'
    harga_booking_rupiah.admin_order_field = 'harga_booking'

@admin.register(DailyCapacity)
class DailyCapacityAdmin(admin.ModelAdmin):
    list_display = ('layanan_penitipan', 'tanggal', 'kapasitas_tersedia')
    list_filter = ('layanan_penitipan', 'tanggal')
    search_fields = ('layanan_penitipan__jenis_penitipan', 'tanggal')
    ordering = ('tanggal', 'layanan_penitipan__jenis_penitipan')