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
    """Filters structured item records rendering them onto leaflet matrices with optional distance sorting."""
    query = request.GET.get('q', '').strip()
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
    results = ItemReport.objects.filter(status=ItemReport.StatusType.ACTIVE).order_by('-date_reported')
    
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location_name__icontains=query)
        )
    
    # Enrich results with distance if user location is provided
    if user_lat and user_lon:
        try:
            u_lat = float(user_lat)
            u_lon = float(user_lon)
            for report in results:
                if report.latitude and report.longitude:
                    report.distance = calculate_distance(u_lat, u_lon, report.latitude, report.longitude)
                else:
                    report.distance = None
            
            # Sort by distance (optional, keeping date as primary for now unless specific sorting requested)
            # results = sorted(results, key=lambda x: x.distance if x.distance is not None else 999999)
        except (ValueError, TypeError):
            pass

    return render(request, 'tracker/search.html', {
        'results': results, 
        'query': query,
        'has_user_location': bool(user_lat and user_lon)
    })

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
    """Loads deeply associative relationships for user records (messages + items) with enhanced stats."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    my_reports = ItemReport.objects.filter(user=request.user).order_by('-date_reported')
    received_msgs = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    
    # Calculate professional stats
    stats = {
        'total_reports': my_reports.count(),
        'resolved_reports': my_reports.filter(status=ItemReport.StatusType.RESOLVED).count(),
        'received_messages': received_msgs.count(),
    }
    
    # Mock activity timeline based on existing records
    activity = []
    for report in my_reports[:5]:
        activity.append({
            'type': 'report',
            'title': f"Reported: {report.title}",
            'date': report.date_reported,
            'status': report.get_status_display()
        })
    for msg in received_msgs[:5]:
        activity.append({
            'type': 'message',
            'title': f"Received message from {msg.sender.username}",
            'date': msg.timestamp,
        })
    
    activity = sorted(activity, key=lambda x: x['date'], reverse=True)[:8]

    return render(request, 'tracker/profile.html', {
        'profile': profile,
        'my_reports': my_reports,
        'received_msgs': received_msgs,
        'stats': stats,
        'activity': activity
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

@login_required(login_url='login')
def resolve_item(request, report_id):
    """Allows owners to mark their item reports as resolved for system finality."""
    report = get_object_or_404(ItemReport, id=report_id, user=request.user)
    report.status = ItemReport.StatusType.RESOLVED
    report.save()
    messages.success(request, f"Congratulations! {report.title} has been marked as resolved.")
    return redirect('profile')
