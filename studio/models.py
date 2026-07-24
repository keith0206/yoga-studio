from django.conf import settings
from django.db import models


class Studio(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
    )
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassType(models.Model):
    name = models.CharField(max_length=80)
    duration_minutes = models.PositiveIntegerField(default=60)
    default_expected_students = models.PositiveIntegerField(default=12)
    color_key = models.CharField(
        max_length=20,
        default="vinyasa",
        help_text="CSS class key: vinyasa, yin, beginner, restore",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassSession(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CANCELLED = "CANCELLED", "Cancelled"

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name="sessions")
    class_type = models.ForeignKey(
        ClassType, on_delete=models.PROTECT, related_name="sessions"
    )
    original_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="original_sessions",
    )
    substitute_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="substitute_sessions",
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    expected_students = models.PositiveIntegerField(default=12)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at"]

    def __str__(self):
        return f"{self.class_type} @ {self.studio} ({self.start_at:%Y-%m-%d %H:%M})"

    @property
    def teaching_teacher(self):
        return self.substitute_teacher or self.original_teacher

    @property
    def students_display(self):
        try:
            return self.attendance.students_attended
        except StudentAttendance.DoesNotExist:
            return self.expected_students


class StudentAttendance(models.Model):
    class_session = models.OneToOneField(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="attendance",
    )
    students_attended = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_attendances",
    )
    confirmed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.class_session} — {self.students_attended} students"
