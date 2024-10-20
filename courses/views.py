from django.shortcuts import render, HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Period, Course, Day
from .serializer import PeriodSerializer
from collections import defaultdict


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer

    @action(detail=False, methods=["post"], url_path="create-periods")
    def create_periods(self, request):
        course_id = request.data.get("course_id")

        try:
            course = Course.objects.get(id=course_id)

            subjects = course.subjects.all()
            subject_count = subjects.count()

            if subject_count == 0:
                return Response(
                    {"error": "No subjects available for this course."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            staff_mapping = {subject: subject.staff.all() for subject in subjects}

            days_of_week = Day.objects.all().order_by("name")
            period_slots = [
                "10:00 - 11:00",
                "11:00 - 12:00",
                "02:00 - 03:00",
                "03:00 - 04:00",
            ]

            period_data = []
            total_periods = 20  # 4 periods per day, 5 days a week
            periods_per_day = len(period_slots)

            # Create a counter to distribute subjects
            subject_cycle = list(subjects) * (
                total_periods // subject_count + 1
            )  # Repeat subjects if needed
            period_index = 0

            # Assign periods for each day and period slot
            for day in days_of_week:
                for slot in period_slots:
                    if period_index >= total_periods:
                        break

                    # Get the current subject for this period
                    subject = subject_cycle[period_index]
                    staff_list = staff_mapping[subject]
                    if not staff_list.exists():
                        return Response(
                            {"error": f"No staff available for subject: {subject}"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    staff = (
                        staff_list.first()
                    )  # Choose the first staff member for simplicity

                    period_data.append(
                        Period(
                            course=course,
                            subject=subject,
                            staff=staff,
                            day=day,
                            period_slot=slot,
                        )
                    )

                    period_index += 1

            # Bulk create all period instances
            Period.objects.bulk_create(period_data)

            return Response(
                {"message": "Periods created successfully."},
                status=status.HTTP_201_CREATED,
            )

        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        #     days_of_week = ["MON", "TUE", "WED", "THU", "FRI"]
        #     period_slots = [
        #         "10:00 - 11:00",
        #         "11:00 - 12:00",
        #         "02:00 - 03:00",
        #         "03:00 - 04:00",
        #     ]

        #     created_periods = []

        #     # Get the subjects related to the course
        #     subjects = course.subjects.all()
        #     print("--------------------------------", subjects)

        #     for day in days_of_week:

        #         day_instance = Day.objects.get(name=day)

        #         for subject in subjects:
        #             # Get the staff associated with the subject
        #             staff_members = subject.staff.all()

        #             # If staff exists for the subject, proceed
        #             if staff_members.exists():
        #                 staff = staff_members.first()

        #                 for period_slot in period_slots:
        #                     if not Period.objects.filter(
        #                         course=course, day=day_instance, period_slot=period_slot
        #                     ).exists():
        #                         period = Period.objects.create(
        #                             course=course,
        #                             day=day_instance,
        #                             period_slot=period_slot,
        #                             staff=staff,
        #                             subject=subject,
        #                         )
        #                         created_periods.append(period)

        #     serializer = self.get_serializer(created_periods, many=True)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # except Course.DoesNotExist:
        #     return Response(
        #         {"error": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND
        #     )
