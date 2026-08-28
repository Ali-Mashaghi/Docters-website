from django.db.models import Count, Q

from apps.consultations.models import ConsultationRequest
from apps.doctors.models import Doctor


def get_accessible_doctors(user):
    """Return doctors the user is allowed to manage."""
    if user.is_superuser:
        return Doctor.objects.all()
    if user.is_staff:
        return Doctor.objects.filter(managers__user=user).distinct()
    return Doctor.objects.none()


def get_accessible_consultations(user):
    """Return consultation requests scoped to user's doctor access."""
    if user.is_superuser:
        return ConsultationRequest.objects.select_related("doctor")
    if user.is_staff:
        return ConsultationRequest.objects.filter(
            doctor__managers__user=user
        ).select_related("doctor").distinct()
    return ConsultationRequest.objects.none()


def user_can_access_consultation(user, consultation_id):
    """Check if user can access a specific consultation request."""
    return get_accessible_consultations(user).filter(pk=consultation_id).exists()


def user_can_access_doctor(user, doctor_id):
    """Check if user can access a specific doctor."""
    return get_accessible_doctors(user).filter(pk=doctor_id).exists()


def get_dashboard_stats(user):
    """Aggregate dashboard statistics for the current user."""
    doctors = get_accessible_doctors(user)
    consultations = get_accessible_consultations(user)

    return {
        "doctor_count": doctors.count(),
        "total_requests": consultations.count(),
        "pending_requests": consultations.filter(status="pending").count(),
        "completed_requests": consultations.filter(status="completed").count(),
        "contacted_requests": consultations.filter(status="contacted").count(),
    }
