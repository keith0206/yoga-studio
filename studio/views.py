from calendar import monthrange
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AddTeacherForm,
    ConfirmAttendanceForm,
    EditTeacherLoginForm,
    QuickAddClassForm,
)
from .models import ClassSession, ClassType, StudentAttendance, Studio, Teacher


def _month_choices(n=12):
    today = timezone.localdate()
    choices = []
    year, month = today.year, today.month
    for _ in range(n):
        label = date(year, month, 1).strftime("%B %Y")
        value = f"{year:04d}-{month:02d}"
        choices.append((value, label))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return choices


def _parse_month(value):
    today = timezone.localdate()
    if not value:
        return today.year, today.month
    try:
        year_s, month_s = value.split("-")
        return int(year_s), int(month_s)
    except (ValueError, AttributeError):
        return today.year, today.month


def _week_start(d):
    return d - timedelta(days=d.weekday())


def _split_day_bands(day_sessions):
    """Split sessions into morning (< noon) and afternoon (noon onward), already time-ordered."""
    morning, afternoon = [], []
    for s in day_sessions:
        local = timezone.localtime(s.start_at)
        if local.hour < 12:
            morning.append(s)
        else:
            afternoon.append(s)
    return morning, afternoon


def _owner_required(user):
    return user.is_authenticated and user.is_owner


@login_required
def home(request):
    if request.user.is_teacher and not request.user.is_owner:
        return redirect("attendance")
    return redirect("dashboard")


@login_required
def dashboard(request):
    if not _owner_required(request.user):
        return redirect("attendance")

    month_value = request.GET.get("month")
    year, month = _parse_month(month_value)
    studio_id = request.GET.get("studio") or ""

    start = timezone.make_aware(datetime(year, month, 1))
    last_day = monthrange(year, month)[1]
    end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))

    sessions = (
        ClassSession.objects.filter(
            start_at__gte=start,
            start_at__lte=end,
            status=ClassSession.Status.SCHEDULED,
        )
        .select_related(
            "studio",
            "class_type",
            "original_teacher",
            "substitute_teacher",
            "attendance",
        )
        .order_by("start_at")
    )
    if studio_id:
        sessions = sessions.filter(studio_id=studio_id)

    scheduled = sessions.count()
    confirmed = sessions.filter(attendance__isnull=False).count()
    student_visits = (
        sessions.aggregate(total=Sum("attendance__students_attended"))["total"] or 0
    )
    with_sub = sessions.filter(substitute_teacher__isnull=False).count()

    return render(
        request,
        "studio/dashboard.html",
        {
            "month_choices": _month_choices(),
            "month_value": f"{year:04d}-{month:02d}",
            "studios": Studio.objects.filter(is_active=True),
            "studio_id": studio_id,
            "stats": {
                "scheduled": scheduled,
                "confirmed": confirmed,
                "student_visits": student_visits,
                "with_sub": with_sub,
            },
            "sessions": sessions,
        },
    )


@login_required
def teachers_page(request):
    if not _owner_required(request.user):
        return redirect("attendance")

    month_value = request.GET.get("month")
    year, month = _parse_month(month_value)
    start = timezone.make_aware(datetime(year, month, 1))
    last_day = monthrange(year, month)[1]
    end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))

    teachers = Teacher.objects.filter(is_active=True).select_related("user")
    rows = []
    for teacher in teachers:
        as_original = ClassSession.objects.filter(
            original_teacher=teacher,
            start_at__gte=start,
            start_at__lte=end,
            status=ClassSession.Status.SCHEDULED,
        )
        as_sub = ClassSession.objects.filter(
            substitute_teacher=teacher,
            start_at__gte=start,
            start_at__lte=end,
            status=ClassSession.Status.SCHEDULED,
        )
        taught = ClassSession.objects.filter(
            Q(original_teacher=teacher, substitute_teacher__isnull=True)
            | Q(substitute_teacher=teacher),
            start_at__gte=start,
            start_at__lte=end,
            status=ClassSession.Status.SCHEDULED,
        )
        confirmed = taught.filter(attendance__isnull=False).count()
        visits = (
            taught.aggregate(total=Sum("attendance__students_attended"))["total"] or 0
        )
        rows.append(
            {
                "teacher": teacher,
                "scheduled": as_original.count(),
                "confirmed": confirmed,
                "student_visits": visits,
                "as_substitute": as_sub.count(),
            }
        )

    return render(
        request,
        "studio/teachers.html",
        {
            "month_choices": _month_choices(),
            "month_value": f"{year:04d}-{month:02d}",
            "rows": rows,
            "add_form": AddTeacherForm(),
        },
    )


@login_required
@require_POST
def teacher_add(request):
    if not _owner_required(request.user):
        return HttpResponseForbidden("Owners only")

    form = AddTeacherForm(request.POST)
    if form.is_valid():
        teacher = form.save()
        messages.success(request, f"Added teacher {teacher.name}.")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    month = request.POST.get("month") or ""
    if month:
        return redirect(f"/teachers/?month={month}")
    return redirect("teachers")


@login_required
@require_POST
def teacher_edit_login(request, teacher_id):
    if not _owner_required(request.user):
        return HttpResponseForbidden("Owners only")

    teacher = get_object_or_404(Teacher, pk=teacher_id, is_active=True)
    form = EditTeacherLoginForm(request.POST, teacher=teacher)
    if form.is_valid():
        form.save()
        messages.success(request, f"Updated login for {teacher.name}.")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    month = request.POST.get("month") or ""
    if month:
        return redirect(f"/teachers/?month={month}")
    return redirect("teachers")


@login_required
@require_POST
def teacher_remove(request, teacher_id):
    if not _owner_required(request.user):
        return HttpResponseForbidden("Owners only")

    teacher = get_object_or_404(Teacher, pk=teacher_id, is_active=True)
    referenced = ClassSession.objects.filter(
        Q(original_teacher=teacher) | Q(substitute_teacher=teacher)
    ).exists()

    if referenced:
        teacher.is_active = False
        teacher.save(update_fields=["is_active"])
        if teacher.user_id:
            user = teacher.user
            user.is_active = False
            user.save(update_fields=["is_active"])
        messages.success(
            request,
            f"Deactivated {teacher.name} (kept for class history).",
        )
    else:
        user = teacher.user
        teacher.delete()
        if user is not None:
            user.delete()
        messages.success(request, f"Removed {teacher.name}.")

    month = request.POST.get("month") or ""
    if month:
        return redirect(f"/teachers/?month={month}")
    return redirect("teachers")


@login_required
def schedule(request):
    week_param = request.GET.get("week")
    today = timezone.localdate()
    if week_param:
        try:
            week_start = date.fromisoformat(week_param)
            week_start = _week_start(week_start)
        except ValueError:
            week_start = _week_start(today)
    else:
        week_start = _week_start(today)

    week_end = week_start + timedelta(days=6)
    start_dt = timezone.make_aware(datetime.combine(week_start, time.min))
    end_dt = timezone.make_aware(datetime.combine(week_end, time.max))

    sessions = (
        ClassSession.objects.filter(
            start_at__gte=start_dt,
            start_at__lte=end_dt,
            status=ClassSession.Status.SCHEDULED,
        )
        .select_related(
            "studio",
            "class_type",
            "original_teacher",
            "substitute_teacher",
            "attendance",
        )
        .order_by("start_at")
    )

    studios = list(Studio.objects.filter(is_active=True))
    days = [week_start + timedelta(days=i) for i in range(7)]

    grid = []
    for studio in studios:
        row = {"studio": studio, "cells": []}
        for day in days:
            day_sessions = [
                s
                for s in sessions
                if s.studio_id == studio.id and timezone.localtime(s.start_at).date() == day
            ]
            morning, afternoon = _split_day_bands(day_sessions)
            row["cells"].append(
                {
                    "date": day,
                    "morning": morning,
                    "afternoon": afternoon,
                    "is_empty": not morning and not afternoon,
                }
            )
        grid.append(row)

    form = QuickAddClassForm(
        initial={
            "date": today,
            "time": time(9, 0),
            "expected_students": 12,
        }
    )

    return render(
        request,
        "studio/schedule.html",
        {
            "week_start": week_start,
            "week_end": week_end,
            "prev_week": week_start - timedelta(days=7),
            "next_week": week_start + timedelta(days=7),
            "days": days,
            "grid": grid,
            "form": form,
            "class_types": ClassType.objects.filter(is_active=True),
            "teachers": Teacher.objects.filter(is_active=True),
            "studios": studios,
            "time_presets": ["09:00", "10:00", "11:00", "17:30", "18:00", "19:00"],
            "can_edit": _owner_required(request.user),
        },
    )


@login_required
@require_POST
def add_class(request):
    if not _owner_required(request.user):
        return HttpResponseForbidden("Owners only")

    form = QuickAddClassForm(request.POST)
    if form.is_valid():
        created = form.save()
        messages.success(
            request,
            f"Added {len(created)} class{'es' if len(created) != 1 else ''}.",
        )
    else:
        messages.error(request, "Could not add class. Check the form and try again.")

    week = request.POST.get("week") or ""
    url = "schedule"
    if week:
        return redirect(f"/schedule/?week={week}")
    return redirect(url)


@login_required
def attendance(request):
    teacher = getattr(request.user, "teacher_profile", None)
    now = timezone.now()
    upcoming_end = now + timedelta(days=14)

    if request.user.is_owner and not teacher:
        sessions = (
            ClassSession.objects.filter(
                start_at__gte=now - timedelta(hours=6),
                start_at__lte=upcoming_end,
                status=ClassSession.Status.SCHEDULED,
            )
            .select_related(
                "studio",
                "class_type",
                "original_teacher",
                "substitute_teacher",
                "attendance",
            )
            .order_by("start_at")[:30]
        )
        role_note = "Owner view — all upcoming classes"
    elif teacher:
        sessions = (
            ClassSession.objects.filter(
                Q(original_teacher=teacher, substitute_teacher__isnull=True)
                | Q(substitute_teacher=teacher),
                start_at__gte=now - timedelta(hours=6),
                start_at__lte=upcoming_end,
                status=ClassSession.Status.SCHEDULED,
            )
            .select_related(
                "studio",
                "class_type",
                "original_teacher",
                "substitute_teacher",
                "attendance",
            )
            .order_by("start_at")
        )
        role_note = "Your upcoming classes"
    else:
        sessions = ClassSession.objects.none()
        role_note = "No teacher profile linked to this account."

    return render(
        request,
        "studio/attendance.html",
        {
            "sessions": sessions,
            "role_note": role_note,
            "teacher": teacher,
        },
    )


@login_required
@require_POST
def confirm_attendance(request, session_id):
    session = get_object_or_404(
        ClassSession.objects.select_related("original_teacher", "substitute_teacher"),
        pk=session_id,
        status=ClassSession.Status.SCHEDULED,
    )
    teacher = getattr(request.user, "teacher_profile", None)
    allowed = request.user.is_owner
    if teacher and session.teaching_teacher_id == teacher.id:
        allowed = True
    if not allowed:
        return HttpResponseForbidden("Not allowed")

    form = ConfirmAttendanceForm(request.POST)
    if form.is_valid():
        StudentAttendance.objects.update_or_create(
            class_session=session,
            defaults={
                "students_attended": form.cleaned_data["students_attended"],
                "confirmed_by": request.user,
            },
        )
        messages.success(request, "Attendance confirmed.")
    else:
        messages.error(request, "Enter a valid student count.")
    return redirect("attendance")


@login_required
@require_POST
def apply_leave(request):
    messages.info(
        request,
        "Leave request — coming soon. Full leave & cover flow will be added later.",
    )
    return redirect("attendance")

