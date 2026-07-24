from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        TEACHER = "TEACHER", "Teacher"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OWNER,
    )

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
