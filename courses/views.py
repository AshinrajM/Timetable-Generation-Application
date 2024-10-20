from django.shortcuts import render, HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Period, Course, Day, Staff
from .serializer import PeriodSerializer, CourseSerializer, StaffSerializer
from collections import defaultdict


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new course.
            request: The request object containing course data.
            Response: A response object containing the created course data or error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update an existing course.
            request: The request object containing updated course data.
            pk: The primary key of the course to update.
            Response: A response object containing the updated course data or error.
        """
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Delete a course.
            request: The request object.
            pk: The primary key of the course to delete.
            Response: A response object with a 204 status code.
        """
        course = self.get_object()
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffViewSet(viewsets.ModelViewSet):

    """
    A viewset for managing staff members.

    This viewset provides actions to create, retrieve, update, and delete 
    staff members. Each staff member can be associated with multiple subjects.

    Methods:
        create: Create a new staff member.
        update: Update an existing staff member.
        destroy: Delete a staff member.
    """

    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        staff = self.get_object()
        serializer = self.get_serializer(staff, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        staff = self.get_object()
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PeriodViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing periods in a timetable.

    This viewset provides actions to create and  update 
    periods associated with courses. It allows bulk creation of periods 
    based on the subjects of a course and can update existing periods.

    Methods:
        create_periods: Create multiple periods for a specified course.
        update_period: Update an existing period's staff and time slot.
    """
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

    @action(detail=True, methods=["patch"], url_path="update-period")
    def update_period(self, request, pk=None):

        period_slot = request.data.get("period_slot")
        staff_id = request.data.get("staff")

        if not period_slot or not staff_id:
            return Response(
                {"error": "Period slot and staff ID must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            period = Period.objects.get(id=pk)
            staff = Staff.objects.get(id=staff_id)

            if staff not in period.subject.staff.all():
                return Response(
                    {
                        "error": f"Staff {staff.name} is not associated with subject {period.subject.name}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            period.staff = staff
            period.period_slot = period_slot
            period.save()

            return Response(PeriodSerializer(period).data, status=status.HTTP_200_OK)

        except Period.DoesNotExist:
            return Response(
                {"error": "Period not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Staff.DoesNotExist:
            return Response(
                {"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
