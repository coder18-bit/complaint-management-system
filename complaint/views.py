from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Complaint, Engineer, ComplaintHistory
from .forms import ComplaintForm, UpdateComplaintForm, AddEngineerForm
from django.db import models
from django.db.models import Q
from .forms import ComplaintForm, UpdateComplaintForm, AddEngineerForm, AdminUpdateComplaintForm
from django.core.paginator import Paginator


def is_admin(user):
    return user.is_staff or user.is_superuser

def get_engineer(user):
    try:
        return Engineer.objects.get(user=user)
    except Engineer.DoesNotExist:
        return None


@login_required
def dashboard(request):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    engineer = get_engineer(request.user)
    if engineer:
        return redirect('engineer_dashboard')
    messages.error(request, 'No engineer profile found. Contact admin.')
    logout(request)
    return redirect('login')


# ── ADMIN VIEWS ──────────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return redirect('engineer_dashboard')
    complaints_list = Complaint.objects.all().order_by('-created_at')
    paginator = Paginator(complaints_list, 10)  # 10 complaints per page
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)
    stats = {
        'total': complaints_list.count(),
        'open': complaints_list.filter(status='open').count(),
        'in_progress': complaints_list.filter(status='in_progress').count(),
        'resolved': complaints_list.filter(status='resolved').count(),
    }
    return render(request, 'complaint/admin_dashboard.html', {
        'complaints': complaints,
        'stats': stats,
    })


@login_required
def admin_register_complaint(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.registered_by = request.user
            complaint.save()
            ComplaintHistory.objects.create(
                complaint=complaint, changed_by=request.user,
                note="Complaint registered by admin.", new_status='open'
            )
            messages.success(request, f'Complaint #{complaint.id} registered.')
            return redirect('admin_dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'complaint/complaint_form.html', {
        'form': form, 'title': 'Register Complaint (Admin)'
    })


@login_required
def admin_complaint_detail(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    complaint = get_object_or_404(Complaint, pk=pk)
    history = complaint.history.all().order_by('-timestamp')
    return render(request, 'complaint/admin_complaint_detail.html', {
        'complaint': complaint, 'history': history
    })

@login_required
def admin_update_complaint(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')

    complaint = get_object_or_404(Complaint, pk=pk)

    if request.method == 'POST':
        form = AdminUpdateComplaintForm(
            request.POST,
            instance=complaint
        )

        if form.is_valid():
            old_status = complaint.status
            print("STATUS FROM FORM:", form.cleaned_data['status'])

            updated = form.save()

            ComplaintHistory.objects.create(
                complaint=updated,
                changed_by=request.user,
                note="Complaint updated by admin.",
                old_status=old_status,
                new_status=updated.status
            )

            messages.success(request, "Complaint updated successfully.")
            return redirect('admin_complaint_detail', pk=updated.pk)

    else:
        form = AdminUpdateComplaintForm(instance=complaint)

    return render(
        request,
        'complaint/admin_update_complaint.html',
        {
            'form': form,
            'complaint': complaint
        }
    )


@login_required
def engineer_list(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    engineers = Engineer.objects.select_related('user').all()
    return render(request, 'complaint/engineer_list.html', {'engineers': engineers})


@login_required
def add_engineer(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        form = AddEngineerForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                )
                Engineer.objects.create(
                    user=user,
                    phone=form.cleaned_data['phone'],
                    department=form.cleaned_data['department'],
                )
                messages.success(request, f"Engineer '{user.username}' added.")
                return redirect('engineer_list')
    else:
        form = AddEngineerForm()
    return render(request, 'complaint/add_engineer.html', {'form': form})


@login_required
def edit_engineer(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')

    engineer = get_object_or_404(Engineer, pk=pk)
    user = engineer.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        engineer.phone = request.POST.get('phone')
        engineer.department = request.POST.get('department')

        user.save()
        engineer.save()

        messages.success(request, 'Engineer updated successfully.')
        return redirect('engineer_list')

    context = {
        'engineer': engineer
    }
    return render(request, 'complaint/edit_engineer.html', context)

# ── ENGINEER VIEWS ───────────────────────────────────────────────────────────

@login_required
def engineer_dashboard(request):
    engineer = get_engineer(request.user)
    if not engineer:
        logout(request)
        return redirect('login')
    
    complaints_list = Complaint.objects.filter(
    models.Q(assigned_to=engineer) |
    models.Q(forwarded_by=engineer)
).distinct().order_by('-created_at')
    paginator = Paginator(complaints_list, 10)
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)
    stats = {
        'total': complaints_list.count(),
        'open': complaints_list.filter(status='open').count(),
        'in_progress': complaints_list.filter(status='in_progress').count(),
        'resolved': complaints_list.filter(status='resolved').count(),
    }
    return render(request, 'complaint/engineer_dashboard.html', {
        'complaints': complaints, 'engineer': engineer, 'stats': stats
    })


@login_required
def engineer_register_complaint(request):
    engineer = get_engineer(request.user)
    if not engineer:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)

            complaint.registered_by = request.user
            if not complaint.assigned_to:
                complaint.assigned_to = engineer
            complaint.save()
            ComplaintHistory.objects.create(
                complaint=complaint, changed_by=request.user,
                note="Complaint registered by engineer.", new_status='open'
            )
            messages.success(request, f'Complaint #{complaint.id} registered.')
            return redirect('engineer_dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'complaint/complaint_form.html', {
        'form': form, 'title': 'Register New Complaint'
    })


@login_required
def engineer_complaint_detail(request, pk):
    engineer = get_engineer(request.user)
    if not engineer:
        return redirect('dashboard')
    complaint = get_object_or_404(
    Complaint,
    Q(assigned_to=engineer) | Q(forwarded_by=engineer),
    pk=pk
)
    is_current_assignee = (complaint.assigned_to == engineer)
    history = complaint.history.all().order_by('-timestamp')
    if request.method == 'POST':
        if not is_current_assignee:
            messages.error(request, "You cannot modify a forwarded complaint.")
            return redirect('engineer_dashboard')
        form = UpdateComplaintForm(request.POST, instance=complaint, current_engineer=engineer)
        if form.is_valid():
            complaint.refresh_from_db()
            old_status = complaint.status
            old_assignee = complaint.assigned_to
            # Explicitly update assignee from cleaned_data before saving.
# Required because assigned_to was not being updated correctly by form.save(commit=False).
            updated = form.save(commit=False)
            updated.assigned_to = form.cleaned_data['assigned_to']
            if updated.assigned_to and updated.assigned_to != old_assignee:
                updated.forwarded_by = engineer
            if updated.assigned_to is None:
                updated.assigned_to = engineer
            if updated.status == 'resolved' and not complaint.resolved_at:
                updated.resolved_at = timezone.now()
                print("ENGINEER STATUS:", updated.status)
            updated.save()
            ComplaintHistory.objects.create(
                complaint=updated, changed_by=request.user,
                note=form.cleaned_data['note'],
                old_status=old_status, new_status=updated.status
            )
            messages.success(request, 'Complaint updated.')
            return redirect('engineer_dashboard')
    else:
        form = UpdateComplaintForm(instance=complaint, current_engineer=engineer)
    return render(request, 'complaint/engineer_complaint_detail.html', {
        'complaint': complaint, 'history': history, 'form': form, 'is_current_assignee': is_current_assignee,
    })