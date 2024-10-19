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
    PERIOD_CHOICES = [
        ("10:00 - 11:00", "10:00 - 11:00"),
        ("11:00 - 12:00", "11:00 - 12:00"),
        ("02:00 - 03:00", "02:00 - 03:00"),
        ("03:00 - 04:00", "03:00 - 04:00"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    period_slot = models.CharField(max_length=20, choices=PERIOD_CHOICES)

    class Meta:
        unique_together = ("course", "day", "period_slot")

    def __str__(self):
        return f"{self.course} - {self.day} - {self.period_slot}"
