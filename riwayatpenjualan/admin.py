from django.contrib import admin
from .models import RiwayatPenjualan
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

# Register your models here.
class RiwayatPenjualanAdmin(admin.ModelAdmin):
    list_display = (
        'id_penjualan', 'tanggal_penjualan', 'pelanggan', 'layanan',
        'status', 'total_penjualan_rupiah',
    )
    search_fields = ('pelanggan', 'layanan')
    list_filter = (
      'status',
        ('tanggal_penjualan', DateRangeFilter),  # Menggunakan DateRangeFilter daripada DateTimeRangeFilter
    )
    
    # Tambahkan Media class untuk memastikan search bekerja dengan DateRangeFilter
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/core.js',
        )
    ordering = ('-tanggal_penjualan',)

    # Mencegah penambahan, pengeditan, dan penghapusan data
    def has_add_permission(self, request):
        # Tidak mengizinkan siapapun untuk menambahkan data
        return False
    
    def has_change_permission(self, request, obj=None):
        # Tidak mengizinkan siapapun untuk mengubah data
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Tidak mengizinkan siapapun untuk menghapus data
        return False
        
    # Tetap mengizinkan melihat modul dan data
    def has_module_permission(self, request):
        # Hanya tampilkan menu jika user adalah superuser atau staff
        return request.user.is_superuser or request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        # Mengizinkan superuser dan staff untuk melihat data
        return request.user.is_superuser or request.user.is_staff
    
    # Format total penjualan ke format rupiah
    def total_penjualan_rupiah(self, obj):
        
        value = int(obj.total_penjualan)
        rupiah = f"Rp {value:,}".replace(",", ".")
        return format_html('<span>{}</span>', rupiah)
    total_penjualan_rupiah.short_description = 'Total Penjualan'
    total_penjualan_rupiah.admin_order_field = 'total_penjualan'
    
    # Override get_search_results untuk memperbaiki pencarian dengan DateRangeFilter
    def get_search_results(self, request, queryset, search_term):
        # Panggil metode asli terlebih dahulu
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Jika ada search term dan tidak ada hasil, coba tambahan pencarian
        if search_term and not queryset.exists():
            # Coba cari berdasarkan status (completed/cancelled)
            if 'selesai' in search_term.lower():
                queryset |= self.model.objects.filter(status='completed')
            elif 'dibatalkan' in search_term.lower():
                queryset |= self.model.objects.filter(status='cancelled')
                
        return queryset, use_distinct
    
    # Tambahkan aksi untuk ekspor data
    actions = ['export_as_csv', 'export_as_pdf']
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=riwayat_penjualan.csv'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Tanggal', 'Pelanggan', 'Layanan', 'Status', 'Total'])
        
        for obj in queryset:
            writer.writerow([
                obj.id_penjualan,
                obj.tanggal_penjualan.strftime('%Y-%m-%d %H:%M:%S'),
                obj.pelanggan,
                obj.layanan,
                obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status,
                obj.total_penjualan,
            ])
        
        return response
    export_as_csv.short_description = "Export Selected to CSV"
    
    def _get_date_range(self, request):
        """
        Helper method to extract date range from request
        """
        from datetime import datetime
        import re
        import urllib.parse
        
        tanggal_awal = None
        tanggal_akhir = None
        
        # Dapatkan semua parameter dari request
        all_params = request.GET.copy()
        for key, value in all_params.items():
            print(f"Request parameter: {key}={value}")
            
        # Metode 1: Periksa parameter langsung dari DateRangeFilter
        # Parameter dari DateRangeFilter berbeda dari DateTimeRangeFilter
        if 'tanggal_penjualan__range__gte' in request.GET:
            try:
                tanggal_awal_str = request.GET.get('tanggal_penjualan__range__gte')
                tanggal_akhir_str = request.GET.get('tanggal_penjualan__range__lte')
                
                if tanggal_awal_str:
                    tanggal_awal = datetime.strptime(tanggal_awal_str, '%d-%m-%Y')
                if tanggal_akhir_str:
                    tanggal_akhir = datetime.strptime(tanggal_akhir_str, '%d-%m-%Y')
                print(f"Method 1: Found date range: {tanggal_awal} - {tanggal_akhir}")
            except Exception as e:
                print(f"Error parsing direct GET params: {e}")
        
        # Metode 2: Periksa parameter alternatif dari DateRangeFilter
        if not tanggal_awal and ('tanggal_penjualan__gte' in request.GET or 'tanggal_penjualan__lte' in request.GET):
            try:
                tanggal_awal_str = request.GET.get('tanggal_penjualan__gte')
                tanggal_akhir_str = request.GET.get('tanggal_penjualan__lte')
                
                if tanggal_awal_str:
                    tanggal_awal = datetime.strptime(tanggal_awal_str, '%d-%m-%Y')
                if tanggal_akhir_str:
                    tanggal_akhir = datetime.strptime(tanggal_akhir_str, '%d-%m-%Y')
                print(f"Method 2: Found date range: {tanggal_awal} - {tanggal_akhir}")
            except Exception as e:
                print(f"Error parsing standard date filter: {e}")
        
        # Metode 3: Periksa _changelist_filters (encoded URL parameters)
        if not tanggal_awal:
            filter_str = request.GET.get('_changelist_filters', '')
            print(f"_changelist_filters: {filter_str}")
            
            if filter_str:
                # Decode filter string jika perlu
                try:
                    filter_parts = filter_str.split('&')
                    for part in filter_parts:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            decoded_key = urllib.parse.unquote(key)
                            decoded_value = urllib.parse.unquote(value)
                            print(f"Filter part: {decoded_key}={decoded_value}")
                            
                            # Check for date parameters
                            if decoded_key in ('tanggal_penjualan__range__gte', 'tanggal_penjualan__gte'):
                                tanggal_awal = datetime.strptime(decoded_value, '%d-%m-%Y')
                            elif decoded_key in ('tanggal_penjualan__range__lte', 'tanggal_penjualan__lte'):
                                tanggal_akhir = datetime.strptime(decoded_value, '%d-%m-%Y')
                    print(f"Method 3: Found date range: {tanggal_awal} - {tanggal_akhir}")
                except Exception as e:
                    print(f"Error parsing filter string: {e}")
                    
        print(f"Final date range: {tanggal_awal} - {tanggal_akhir}")
        return tanggal_awal, tanggal_akhir
    
    def export_as_pdf(self, request, queryset):
        from django.http import HttpResponse
        from django.template.loader import render_to_string
        import weasyprint
        from decimal import Decimal
        from datetime import datetime
        
        # Ambil parameter filter tanggal jika ada
        tanggal_awal, tanggal_akhir = self._get_date_range(request)
        
        # Debug log untuk memastikan kita dapat mengekstrak tanggal
        print(f"===== DEBUG EXPORT PDF =====")
        print(f"Request GET: {request.GET}")
        print(f"Extracted date range: {tanggal_awal} - {tanggal_akhir}")
        
        # Hitung total pendapatanfrom django.utils.html import format_html
        total_pendapatan = Decimal('0.00')
        for obj in queryset:
            if obj.status == 'completed':  # Hanya hitung penjualan yang selesai
                total_pendapatan += obj.total_penjualan
        
        # Format data dengan format Rupiah
        data_with_format = []
        for obj in queryset:
            obj_dict = {
                'id_penjualan': obj.id_penjualan,
                'tanggal_penjualan': obj.tanggal_penjualan,
                'pelanggan': obj.pelanggan,
                'layanan': obj.layanan,
                'status': obj.status,
                'total_penjualan': obj.total_penjualan,
                'total_penjualan_rupiah': f"Rp {int(obj.total_penjualan):,}".replace(",", ".")
            }
            data_with_format.append(obj_dict)
        
        # Format total pendapatan ke Rupiah
        total_pendapatan_rupiah = f"Rp {int(total_pendapatan):,}".replace(",", ".")
        
        # Nama file berisi tanggal jika ada filter tanggal
        filename_prefix = 'laporan_penjualan'
        if tanggal_awal and tanggal_akhir:
            filename_prefix = f'laporan_penjualan_{tanggal_awal.strftime("%Y%m%d")}_sd_{tanggal_akhir.strftime("%Y%m%d")}'
        elif tanggal_awal:
            filename_prefix = f'laporan_penjualan_dari_{tanggal_awal.strftime("%Y%m%d")}'
        elif tanggal_akhir:
            filename_prefix = f'laporan_penjualan_sampai_{tanggal_akhir.strftime("%Y%m%d")}'
        
        # Render ke HTML - Pastikan tanggal_awal dan tanggal_akhir diteruskan dengan benar
        context = {
            'data': data_with_format,
            'total_pendapatan': total_pendapatan,
            'total_pendapatan_rupiah': total_pendapatan_rupiah,
            'tanggal_awal': tanggal_awal,
            'tanggal_akhir': tanggal_akhir,
        }
        
        # Debug info for template context
        print(f"Context keys: {context.keys()}")
        print(f"tanggal_awal: {tanggal_awal}, tanggal_akhir: {tanggal_akhir}")
        print(f"tanggal_awal type: {type(tanggal_awal)}, tanggal_akhir type: {type(tanggal_akhir)}")

        # Jika tanggal tidak ditemukan lewat filter, coba lihat langsung dari selected_filters
        if not tanggal_awal and not tanggal_akhir and hasattr(request, 'admin_site'):
            cl = self.get_changelist_instance(request)
            if hasattr(cl, 'get_filters_params'):
                params = cl.get_filters_params()
                print(f"Changelist filter params: {params}")
                for key, value in params.items():
                    print(f"{key}: {value}")

        html_string = render_to_string('riwayatpenjualan/laporan_pdf.html', context)
        
        # Log untuk debugging template
        print(f"HTML Preview (first 200 chars): {html_string[:200]}...")

        # Buat PDF
        pdf_file = weasyprint.HTML(string=html_string).write_pdf()
        
        # Return sebagai response
        filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        print(f"Generated filename: {filename}")
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    export_as_pdf.short_description = "Export Selected to PDF"

admin.site.register(RiwayatPenjualan, RiwayatPenjualanAdmin)