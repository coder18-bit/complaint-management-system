from django import forms
from django.contrib.auth.models import User
from .models import Complaint, Engineer
from django.core.exceptions import ValidationError


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'priority', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

class UpdateComplaintForm(forms.ModelForm):
    note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )
    

    class Meta:
        model = Complaint
        fields = ['status', 'assigned_to', 'note']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        current_engineer = kwargs.pop('current_engineer', None)
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].label = "Forward To"
        if self.instance and self.instance.assigned_to:
            self.initial['assigned_to'] = self.instance.assigned_to
        if current_engineer:
            self.fields['assigned_to'].queryset = Engineer.objects.exclude(id=current_engineer.id)
            current_status = self.instance.status
            if current_status == "open":
                if self.instance.assigned_to:
                    allowed = ["in_progress", "Cancel", "resolved"]
                else:
                    allowed = ["open", "in_progress", "Cancel", "resolved"]
            elif current_status == "in_progress":
                allowed = ["in_progress", "Cancel", "resolved"]
            elif current_status == "Cancel":
                allowed = ["open"]
            elif current_status == "resolved":
                allowed = ["resolved"]
            self.fields['status'].choices = [
    choice for choice in Complaint.STATUS_CHOICES
    if choice[0] in allowed
]
            if self.instance.status == "Cancel":
                self.fields['assigned_to'].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        current_status = self.instance.status
        new_status = cleaned_data.get("status")
        if current_status == "resolved" and new_status != "resolved":
            raise ValidationError(
            "Resolved complaints cannot be modified."
        )

    # Cannot go back to open
        if current_status in ["in_progress", "Cancel"] and new_status == "open":
            raise ValidationError(
            "A complaint cannot be moved back to Open."
        )
        assigned_to = cleaned_data.get("assigned_to")
        if self.instance.status == "Cancel" and assigned_to:
            raise forms.ValidationError(
        "Cancelled complaints cannot be forwarded."
    )
        return cleaned_data

class AddEngineerForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class AdminUpdateComplaintForm(forms.ModelForm):

    class Meta:
        model = Complaint
        fields = [
            'title',
            'description',
            'priority',
            'status',
            'assigned_to'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.status in ["Cancel", "resolved"]:
            self.fields['assigned_to'].disabled = True

        current_status = self.instance.status

        if current_status == "open":
            allowed = ["open", "in_progress", "Cancel", "resolved"]

        elif current_status == "in_progress":
            allowed = ["in_progress","Cancel", "resolved"]

        elif current_status == "Cancel":
            allowed = ["Cancel","open"]

        elif current_status == "resolved":
            allowed = ["resolved"]

        self.fields['status'].choices = [
            choice for choice in Complaint.STATUS_CHOICES
            if choice[0] in allowed
        ]