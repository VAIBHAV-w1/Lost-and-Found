from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .forms import ItemReportForm, CustomUserCreationForm
from .models import ItemReport, UserProfile, Message
from .utils import check_for_matches

def home(request):
    """Renders the standard landing page representing the feature stack."""
    return render(request, 'tracker/home.html')

@login_required(login_url='login')
def report_item(request):
    """Handles submission of natively structured item loss or found reports."""
    if request.method == "POST":
        form = ItemReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            messages.success(request, f"Successfully reported your item: {report.title}")
            
            # Fire background match checks cleanly imported from utils.py
            check_for_matches(report)
            return redirect('report_success')
        else:
            messages.error(request, "There was an error in submitting your report. Please check the fields.")
    else:
        form = ItemReportForm()
    return render(request, 'tracker/report_form.html', {'form': form})

def report_success(request):
    """Secondary dispatch template confirming user submission safely."""
    try:
        report = ItemReport.objects.latest('date_reported')
    except ItemReport.DoesNotExist:
        report = None
    return render(request, 'tracker/success.html', {'report': report})

@login_required(login_url='login')
def search_reports(request):
    """Filters structured item records rendering them onto leaflet matrices."""
    query = request.GET.get('q', '').strip()
    results = ItemReport.objects.filter(status=ItemReport.StatusType.ACTIVE).order_by('-date_reported')
    
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location_name__icontains=query)
        )
    return render(request, 'tracker/search.html', {'results': results, 'query': query})

def signup(request):
    """Authentication handling for structured user profiles."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = form.cleaned_data.get('phone_number')
            UserProfile.objects.create(user=user, phone_number=phone)
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account is cleanly setup.")
            return redirect('home')
        else:
            messages.error(request, "Failed to register correctly. Please review your details.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})

def logout_view(request):
    """Cleans session correctly handling auth routing."""
    logout(request)
    messages.info(request, "Successfully logged out. See you next time!")
    return redirect('login')

@login_required(login_url='login')
def user_profile(request):
    """Loads deeply associative relationships for user records (messages + items)."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    my_reports = ItemReport.objects.filter(user=request.user).order_by('-date_reported')
    received_msgs = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    
    return render(request, 'tracker/profile.html', {
        'profile': profile,
        'my_reports': my_reports,
        'received_msgs': received_msgs
    })
    
@login_required(login_url='login')
def send_message(request, report_id):
    """Constructs internal mapping message dispatchment between separate authenticated users."""
    report = get_object_or_404(ItemReport, id=report_id)
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body and report.user:
            Message.objects.create(
                sender=request.user,
                recipient=report.user,
                item=report,
                body=body
            )
            messages.success(request, f"Your message has been securely sent to the reporter of {report.title}")
            
            # Dispatch structural email update
            if report.user.email:
                try:
                    send_mail(
                        f"New Message regarding {report.title}",
                        f"You have received a new secure message from {request.user.username}:\n\n{body}\n\nLogin to view full details.",
                        settings.DEFAULT_FROM_EMAIL,
                        [report.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
        else:
            messages.error(request, "Cannot dispatch an empty message.")
    return redirect('search_reports')
