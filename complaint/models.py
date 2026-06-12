from django.db import models

# Create your models here.

from django.contrib.auth.models import User
import random
import string

class Engineer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('Cancel', 'Cancel'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    reference_id = models.CharField(
    max_length=15,
    unique=True,
    blank=True,
    null=True
)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    registered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='registered_complaints'
    )
    assigned_to = models.ForeignKey(
        Engineer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_complaints'
    )
    forwarded_by = models.ForeignKey(
    Engineer,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='forwarded_by_me'
)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def generate_reference_id(self):
        while True:
         ref_id = "CMP-" + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

         if not Complaint.objects.filter(reference_id=ref_id).exists():
            return ref_id
    
    def save(self, *args, **kwargs):
        if not self.reference_id:
            self.reference_id = self.generate_reference_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.reference_id} - {self.title}"


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for #{self.complaint.id}"