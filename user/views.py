from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from user.forms import FormAkun
from .models import User


def index(request):
    #cek user login/belum
    if request.user.is_authenticated:
        email = request.user.email
        akun = User.objects.get(email=email)
      
        context = {
            'title':"Profile",
            'akun' : akun,
        }
        return render(request, 'user/index.html',context)
    else:
        return redirect('user:login')
    
def loginView(request):
    error_list = None
    form = FormAkun()
    active_tab = 'login-tab'
    old_data = {}
    if request.method == 'POST':
        if request.POST.get('submit') == 'daftar':
            account_form = FormAkun(request.POST)
            active_tab = 'register-tab'
            old_data = request.POST.dict()
            if account_form.is_valid():
                active_tab = 'login-tab'
                account_form.save()
                messages.success(request, "Berhasil mendaftar silahkan login.")
                return redirect('user:index')
            else:
                error_list = account_form.errors
                form = account_form  # Pass form with errors

        if request.POST.get('submit') == 'masuk':
            username = request.POST['emailform']
            password = request.POST['pwform']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Berhasil login!")
                return redirect('user:index')
            else:
                messages.error(request, "Email atau Password salah!")
                return redirect('user:index')

    context = {
        'title': "Akun login",
        'heading': "Anda Belum Masuk Website!",
        'subheading': "Silahkan Masuk / Mendaftar dibawah.",
        'error': error_list,
        'active_tab': active_tab,
        'old': old_data
    }
    return render(request, 'user/login.html', context)

@login_required
def update_profile(request):
    error_list = {}
    old_data = {}
    if request.method == 'POST':
        if request.POST.get('modalBtn') == 'updateProfile':
            user = request.user
            nama = request.POST.get('nama', '').strip()
            no_hp = request.POST.get('no_hp', '').strip()
            alamat = request.POST.get('alamat', '').strip()
            old_data = request.POST.dict()

            # Validasi manual
            if not nama:
                error_list['nama'] = ['Nama harus diisi.']
            if not no_hp:
                error_list['no_hp'] = ['Nomor telepon harus diisi.']
            if not alamat:
                error_list['alamat'] = ['Alamat harus diisi.']

            if not error_list:
                user.nama = nama
                user.no_hp = no_hp
                user.alamat = alamat
                user.save()
                messages.success(request, 'Profile berhasil diperbarui!')
                return redirect('user:index')
            else:
                # Kirim error ke template
                context = {
                    'title': "Profile",
                    'akun': user,
                    'profile_error': error_list,
                    'profile_old': old_data
                }
                return render(request, 'user/index.html', context)
    return redirect('user:index')

@login_required
def change_password(request):
    password_error = {}
    old_data = {}
    if request.method == 'POST':
        if request.POST.get('modalBtn') == 'updatePassword':
            form = PasswordChangeForm(request.user, request.POST)
            old_data = request.POST.dict()
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password berhasil diperbarui!')
                return redirect('user:index')
            else:
                # Ambil error per field
                for field in form.errors:
                    password_error[field] = form.errors[field]
                context = {
                    'title': "Profile",
                    'akun': request.user,
                    'profile_error': {},
                    'profile_old': {},
                    'password_error': password_error,
                    'password_old': old_data
                }
                return render(request, 'user/index.html', context)
    return redirect('user:index')