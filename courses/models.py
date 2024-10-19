from django.db import models
from django.core.exceptions import ValidationError


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(
        Course, related_name="subjects", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Staff(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject, related_name="staff")

    def __str__(self):
        return self.name


class Day(models.Model):
    DAYS_OF_WEEK = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
    ]
    name = models.CharField(max_length=3, choices=DAYS_OF_WEEK, unique=True)

    def __str__(self):
        return self.name


class Period(models.Model):
    day = models.ForeignKey(Day, related_name="periods", on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["day", "order"]
        unique_together = ["day", "order"]

    def __str__(self):
        return f"{self.day.name} {self.start_time} - {self.end_time}"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("End time must be after start time.")
            
        
        overlapping_periods = Period.objects.filter(
            day=self.day,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping_periods.exists():
            raise ValidationError(_("This period overlaps with an existing period for this day."))
