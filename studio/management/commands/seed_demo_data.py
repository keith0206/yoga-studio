from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time

from accounts.models import User
from studio.models import ClassSession, ClassType, Studio, Teacher


class Command(BaseCommand):
    help = "Seed demo studios, teachers, class types, and a week of classes"

    def handle(self, *args, **options):
        owner, created = User.objects.get_or_create(
            username="owner",
            defaults={
                "email": "admin@studio.local",
                "role": User.Role.OWNER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            owner.set_password("owner123")
            owner.save()
            self.stdout.write("Created owner / owner123")

        admin, admin_created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "owner@studio.local",
                "role": User.Role.OWNER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if admin_created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("Created admin / admin123")
        elif admin.role != User.Role.OWNER or not admin.is_staff:
            admin.role = User.Role.OWNER
            admin.is_staff = True
            admin.is_superuser = True
            admin.save(update_fields=["role", "is_staff", "is_superuser"])
            self.stdout.write("Updated admin account to owner/staff")

        downtown, _ = Studio.objects.get_or_create(name="Downtown")
        west, _ = Studio.objects.get_or_create(name="West Side")

        types = [
            ("Vinyasa", 60, 16, "vinyasa"),
            ("Yin", 60, 12, "yin"),
            ("Beginner", 60, 14, "beginner"),
            ("Restore", 45, 10, "restore"),
        ]
        class_types = {}
        for name, dur, expected, color in types:
            ct, _ = ClassType.objects.get_or_create(
                name=name,
                defaults={
                    "duration_minutes": dur,
                    "default_expected_students": expected,
                    "color_key": color,
                },
            )
            class_types[name] = ct

        teachers_data = [
            ("Jane Lee", "jane@studio.local", "jane", User.Role.TEACHER),
            ("Mark Tan", "mark@studio.local", "mark", User.Role.TEACHER),
            ("Ava Chen", "ava@studio.local", "ava", User.Role.TEACHER),
        ]
        teachers = {}
        for name, email, username, role in teachers_data:
            user, ucreated = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "role": role},
            )
            if ucreated:
                user.set_password("teacher123")
                user.save()
            teacher, _ = Teacher.objects.get_or_create(
                name=name,
                defaults={"email": email, "user": user},
            )
            if not teacher.user_id:
                teacher.user = user
                teacher.save()
            teachers[name] = teacher

        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        plan = [
            (0, downtown, "09:00", "Vinyasa", "Jane Lee"),
            (1, downtown, "10:00", "Yin", "Mark Tan"),
            (2, downtown, "09:00", "Restore", "Jane Lee"),
            (3, downtown, "18:00", "Vinyasa", "Mark Tan"),
            (4, downtown, "09:00", "Beginner", "Jane Lee"),
            (4, downtown, "17:30", "Yin", "Mark Tan"),
            (5, downtown, "10:00", "Vinyasa", "Mark Tan"),
            (6, downtown, "09:30", "Restore", "Jane Lee"),
            (0, west, "11:00", "Yin", "Jane Lee"),
            (1, west, "09:00", "Beginner", "Mark Tan"),
            (2, west, "18:00", "Restore", "Mark Tan"),
            (3, west, "10:00", "Beginner", "Jane Lee"),
            (4, west, "09:00", "Vinyasa", "Mark Tan"),
            (5, west, "11:00", "Yin", "Mark Tan"),
            (6, west, "10:00", "Beginner", "Jane Lee"),
        ]

        created = 0
        for day_offset, studio, time_s, ctype, tname in plan:
            hh, mm = map(int, time_s.split(":"))
            day = week_start + timedelta(days=day_offset)
            start = timezone.make_aware(datetime.combine(day, time(hh, mm)))
            ct = class_types[ctype]
            end = start + timedelta(minutes=ct.duration_minutes)
            _, was_created = ClassSession.objects.get_or_create(
                studio=studio,
                class_type=ct,
                original_teacher=teachers[tname],
                start_at=start,
                defaults={
                    "end_at": end,
                    "expected_students": ct.default_expected_students,
                },
            )
            if was_created:
                created += 1

        # One substitute example
        yin = ClassSession.objects.filter(
            class_type=class_types["Yin"],
            original_teacher=teachers["Mark Tan"],
            studio=downtown,
        ).first()
        if yin and not yin.substitute_teacher_id:
            yin.substitute_teacher = teachers["Ava Chen"]
            yin.save()

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. +{created} classes. "
            "Logins: owner/owner123, admin/admin123, jane/teacher123"
        ))
