import math
import logging
from typing import Optional
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def calculate_distance(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> float:
    """Calculates the geographic distance between two coordinates in kilometers using the Haversine formula."""
    if None in [lat1, lon1, lat2, lon2]:
        return 999999.0
        
    try:
        R = 6371.0 # Radius of Earth in kilometers
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    except (TypeError, ValueError) as exc:
        logger.error(f"Error calculating distance: {exc}")
        return 999999.0

def dispatch_match_email(recipient_email: str, subject_prefix: str, item_title: str, match_details: str) -> None:
    """Helper formatting utility for dispatching emails."""
    try:
        send_mail(
            f"Potential Match Found: {subject_prefix}",
            f"A relevant matching report has been posted near your location.\n\nMatching Item: {item_title}\nContact Info: {match_details}\n\nPlease check your account to connect.",
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=True,
        )
    except Exception as exc:
        logger.error(f"Failed to send match email: {exc}")

def check_for_matches(new_report) -> None:
    """Scans the database for an active item of the opposite report_type and identical category within a 10km radius."""
    from .models import ItemReport
    opposite_type = ItemReport.ReportType.FOUND if new_report.report_type == ItemReport.ReportType.LOST else ItemReport.ReportType.LOST
    
    potential_matches = ItemReport.objects.filter(
        report_type=opposite_type,
        category=new_report.category,
        status=ItemReport.StatusType.ACTIVE
    )
    
    matches = []
    for report in potential_matches:
        dist = calculate_distance(new_report.latitude, new_report.longitude, report.latitude, report.longitude)
        if dist < 10.0:
            matches.append(report)
            
    for match in matches:
        if new_report.user and new_report.user.email:
            dispatch_match_email(new_report.user.email, new_report.title, match.title, match.contact_info)
        
        if match.user and match.user.email:
            dispatch_match_email(match.user.email, match.title, new_report.title, new_report.contact_info)
