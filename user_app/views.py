from django.shortcuts import render

# Create your views here.
def login_view(request):
    return render(request, 'login.html')

def user_dashboard(request):

    return render(request, 'dashboard.html', {'user': request.user})  