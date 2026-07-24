from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("teachers/", views.teachers_page, name="teachers"),
    path("teachers/add/", views.teacher_add, name="teacher_add"),
    path(
        "teachers/<int:teacher_id>/edit-login/",
        views.teacher_edit_login,
        name="teacher_edit_login",
    ),
    path(
        "teachers/<int:teacher_id>/remove/",
        views.teacher_remove,
        name="teacher_remove",
    ),
    path("schedule/", views.schedule, name="schedule"),
    path("schedule/add/", views.add_class, name="add_class"),
    path("attendance/", views.attendance, name="attendance"),
    path(
        "attendance/<int:session_id>/confirm/",
        views.confirm_attendance,
        name="confirm_attendance",
    ),
    path("attendance/apply-leave/", views.apply_leave, name="apply_leave"),
    path("health/", views.health, name="health"),
]
