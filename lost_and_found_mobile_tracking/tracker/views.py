# tracker/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import MobileReportForm
from .models import MobileReport
from django.db.models import Q

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(request):
    return render(request, 'tracker/home.html')

@login_required(login_url='login')
def report_mobile(request):
    if request.method == "POST":
        form = MobileReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('report_success')
    else:
        form = MobileReportForm()

    return render(request, 'tracker/report_form.html', {'form': form})

def report_success(request):
    return render(request, 'tracker/success.html')

@login_required(login_url='login')
def search_reports(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = MobileReport.objects.filter(
            Q(brand__icontains=query) |
            Q(model__icontains=query) |
            Q(imei__icontains=query) |
            Q(color__icontains=query) |
            Q(location__icontains=query)
        )

    return render(request, 'tracker/search.html', {'results': results, 'query': query})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # Replace 'login' with your login URL name


# views.py
def report_success(request):
    # Assuming the report is saved correctly
    report = MobileReport.objects.latest('date_reported')  # Or find the report in a different way if necessary
    return render(request, 'tracker/success.html', {'report': report})

# views.py
from django.shortcuts import render
from .models import UserProfile

def user_profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'tracker/profile.html', {'profile': profile})
