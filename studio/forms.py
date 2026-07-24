from datetime import datetime, timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import ClassSession, ClassType, Studio, Teacher

User = get_user_model()


class QuickAddClassForm(forms.Form):
    studio = forms.ModelChoiceField(queryset=Studio.objects.filter(is_active=True))
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    time = forms.TimeField(widget=forms.HiddenInput())
    class_type = forms.ModelChoiceField(
        queryset=ClassType.objects.filter(is_active=True),
        widget=forms.HiddenInput(),
    )
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.filter(is_active=True))
    expected_students = forms.IntegerField(min_value=0, initial=12)
    repeat_weeks = forms.BooleanField(
        required=False,
        label="Repeat same slot for next 4 weeks",
    )

    def save(self, commit=True):
        data = self.cleaned_data
        class_type = data["class_type"]
        naive = datetime.combine(data["date"], data["time"])
        start = timezone.make_aware(naive)
        end = start + timedelta(minutes=class_type.duration_minutes)
        weeks = 4 if data.get("repeat_weeks") else 1
        created = []
        for week in range(weeks):
            session_start = start + timedelta(weeks=week)
            session_end = end + timedelta(weeks=week)
            session = ClassSession(
                studio=data["studio"],
                class_type=class_type,
                original_teacher=data["teacher"],
                start_at=session_start,
                end_at=session_end,
                expected_students=data["expected_students"],
            )
            if commit:
                session.save()
            created.append(session)
        return created


class ConfirmAttendanceForm(forms.Form):
    students_attended = forms.IntegerField(min_value=0)


class AddTeacherForm(forms.Form):
    name = forms.CharField(max_length=120, label="Name")
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput,
        label="Password",
    )
    email = forms.EmailField(required=False, label="Email (optional)")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    @transaction.atomic
    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            email=data.get("email") or "",
            password=data["password"],
            role=User.Role.TEACHER,
        )
        teacher = Teacher.objects.create(
            user=user,
            name=data["name"],
            email=data.get("email") or "",
            is_active=True,
        )
        return teacher


class EditTeacherLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(
        required=False,
        min_length=6,
        widget=forms.PasswordInput,
        label="New password (leave blank to keep)",
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        if teacher and teacher.user_id and not self.is_bound:
            self.fields["username"].initial = teacher.user.username

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username__iexact=username)
        if self.teacher and self.teacher.user_id:
            qs = qs.exclude(pk=self.teacher.user_id)
        if qs.exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        if self.teacher and not self.teacher.user_id and not cleaned.get("password"):
            self.add_error("password", "Password is required when creating a login.")
        return cleaned

    @transaction.atomic
    def save(self):
        data = self.cleaned_data
        teacher = self.teacher
        if teacher.user_id:
            user = teacher.user
            user.username = data["username"]
            if data.get("password"):
                user.set_password(data["password"])
            user.save()
        else:
            user = User.objects.create_user(
                username=data["username"],
                email=teacher.email or "",
                password=data["password"],
                role=User.Role.TEACHER,
            )
            teacher.user = user
            teacher.save(update_fields=["user"])
        return teacher
