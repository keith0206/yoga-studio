from django.contrib import admin

from .models import ClassSession, ClassType, StudentAttendance, Studio, Teacher


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "address")
    list_filter = ("is_active",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_active", "user")
    list_filter = ("is_active",)
    search_fields = ("name", "email")


@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "default_expected_students", "color_key")


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        "start_at",
        "studio",
        "class_type",
        "original_teacher",
        "substitute_teacher",
        "status",
    )
    list_filter = ("studio", "status", "class_type")
    date_hierarchy = "start_at"


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("class_session", "students_attended", "confirmed_by", "confirmed_at")
