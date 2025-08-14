from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'title': "Syarat dan Ketentuan",
    }
    return render(request, 'home/snkIndex.html', context)