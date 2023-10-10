from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class AbstractTable(models.Model):
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Role(AbstractTable):
    SUPERADMIN = 1
    PROJECT_MANAGER = 2
    ASSISTANT_PROJECT_MANAGER = 3
    TEAM_LEAD = 4
    AGENT = 5

    ROLE_CHOICES = (
        (SUPERADMIN, "Super Admin"),
        (PROJECT_MANAGER, "Project Manager"),
        (ASSISTANT_PROJECT_MANAGER, "Assistant Project Manager"),
        (TEAM_LEAD, "Team Lead"),
        (AGENT, "Agent"),
    )
    role = models.IntegerField(choices=ROLE_CHOICES)

    class Meta:
        db_table = "roles"

    def get_role_display_str(self):
        return dict(self.ROLE_CHOICES).get(self.role)

    def __str__(self):
        return f"{self.get_role_display_str()}"


class Project(AbstractTable):
    project_name = models.CharField(max_length=200)
    project_slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        db_table = "projects"

    def __str__(self):
        return str(self.project_name)


class User(AbstractUser):
    username = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    projects = models.ManyToManyField('Project', related_name='users')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Permission(AbstractTable):
    read = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    update = models.BooleanField(default=False)

    class Meta:
        db_table = "permissions"

class  UserData(AbstractTable):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    STATUS_CHOICES = ((1, "Active"), (0, "Inactive"))
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    class Meta:
        db_table = "user_data"

    def __str__(self):
        return str(self.users.username)
