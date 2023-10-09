from django.contrib import admin
from .models import  UserData, Project, Role,User, Permission

admin.site.register(Permission)
admin.site.register( UserData)
admin.site.register(Project)
admin.site.register(Role)
admin.site.register(User)
