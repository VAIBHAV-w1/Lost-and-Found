from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    """Extended user profile data representing optional contact tracking."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self) -> str:
        if self.user and self.user.username:
            return f"{self.user.username}'s Profile"
        return "Unknown Profile"

class ItemReport(models.Model):
    """Central model tracking natively logged generic Lost and Found reports."""
    
    class ReportType(models.TextChoices):
        LOST = 'lost', _('Lost')
        FOUND = 'found', _('Found')
        
    class CategoryType(models.TextChoices):
        ELECTRONICS = 'electronics', _('Electronics / Mobile')
        WALLET = 'wallet', _('Wallet / Purse')
        KEYS = 'keys', _('Keys')
        PET = 'pet', _('Pet')
        BAG = 'bag', _('Bag / Luggage')
        DOCUMENT = 'document', _('Important Document')
        OTHER = 'other', _('Other')

    class StatusType(models.TextChoices):
        ACTIVE = 'active', _('Active')
        RESOLVED = 'resolved', _('Resolved')

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=10, choices=ReportType.choices)
    category = models.CharField(max_length=20, choices=CategoryType.choices)
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    date_reported = models.DateTimeField(auto_now_add=True)
    item_date = models.DateField(help_text="When was the item lost/found?", null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=StatusType.choices, default=StatusType.ACTIVE)
    contact_info = models.TextField(help_text="How can people contact you? (Email/Phone)")
    photo = models.ImageField(upload_to='item_photos/', null=True, blank=True)

    def __str__(self) -> str:
        report_display = self.get_report_type_display() if self.report_type else "Unknown"
        return f"[{report_display}] {self.title or 'Unnamed Item'}"

class Message(models.Model):
    """Internal user-to-user secure messaging system handling item claims."""
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    item = models.ForeignKey(ItemReport, on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self) -> str:
        sender_name = getattr(self.sender, 'username', 'Unknown Sender')
        recipient_name = getattr(self.recipient, 'username', 'Unknown Recipient')
        return f"Message from {sender_name} to {recipient_name}"
