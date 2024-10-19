from django.contrib import admin
from .models import Course, Subject, Staff, Day, Period


class StaffAdmin(admin.ModelAdmin):
    filter_horizontal = ("subjects",)


admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Day)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Period)
