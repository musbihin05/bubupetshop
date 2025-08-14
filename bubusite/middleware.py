from django.shortcuts import redirect
from django.contrib import messages

class AlreadyLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
     
        # Cek jika user sudah login dan mengakses halaman login
        if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser and request.path == '/user/login':
            messages.info(request, 'Anda sudah login sebagai pelanggan.')
            return redirect('user:index')  # Ganti 'home' dengan nama url tujuan
          
          # Cek jika user sudah login dan mengakses halaman login
        if request.user.is_authenticated and request.user.is_staff and request.user.is_superuser and request.path == '/user/login':
            messages.info(request, 'Anda sudah login sebagai admin.')
            return redirect('admin:index')  # Ganti 'home' dengan nama url tujuan

        response = self.get_response(request)
        return response



class OnlyCustomersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Daftar rute yang hanya boleh diakses oleh pelanggan
        customer_only_routes = [
            '/booking',
            '/peliharaan',
        ]
        
        # Cek apakah path URL dimulai dengan rute yang dibatasi
        is_restricted_route = False
        for route in customer_only_routes:
            if request.path.startswith(route):
                is_restricted_route = True
                break
        
        if is_restricted_route:
            # Cek apakah user adalah admin atau staff
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                messages.info(request, 'Halaman ini hanya dapat diakses oleh pelanggan. Admin dan staff silakan gunakan panel admin.')
                return redirect('home:index')
                
        response = self.get_response(request)
        return response