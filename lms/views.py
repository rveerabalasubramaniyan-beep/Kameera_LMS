from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.db import transaction
from django.db.models import Q, Sum

from django.utils import timezone

from uuid import uuid4


from .models import (
    Course,
    Enrollment,
    StudentProfile,
    Lesson,
    LessonProgress,
    Certificate,
    Batch,
    StudentFee,
    Payment,
)


from .forms import (
    StudentRegistrationForm,
    CourseAdminForm,
    LessonAdminForm,
    BatchAdminForm,
    StudentFeeAdminForm,
    PaymentAdminForm,
)


# ============================================================
# HELPER
# CREATE / GET CERTIFICATE
# ============================================================

def get_or_create_course_certificate(user, course):

    certificate = Certificate.objects.filter(
        user=user,
        course=course
    ).first()

    if certificate:
        return certificate

    total_lessons = Lesson.objects.filter(
        course=course,
        is_active=True
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__course=course,
        lesson__is_active=True,
        completed=True
    ).count()

    if (
        total_lessons == 0
        or completed_lessons < total_lessons
    ):
        return None

    certificate_id = (
        f"KAM-{timezone.now().year}-"
        f"{uuid4().hex[:8].upper()}"
    )

    certificate = Certificate.objects.create(
        user=user,
        course=course,
        certificate_id=certificate_id
    )

    return certificate


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "lms/home.html"
    )


# ============================================================
# COURSE LIST
# ============================================================

def course_list(request):

    courses = Course.objects.filter(
        is_active=True
    )

    return render(
        request,
        "lms/course_list.html",
        {
            "courses": courses
        }
    )


# ============================================================
# COURSE DETAIL
# ============================================================

def course_detail(request, slug):

    course = get_object_or_404(
        Course,
        slug=slug,
        is_active=True
    )

    enrollment = None

    if request.user.is_authenticated:

        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
            is_active=True
        ).first()

    return render(
        request,
        "lms/course_detail.html",
        {
            "course": course,
            "enrollment": enrollment,
        }
    )


# ============================================================
# ENROLL COURSE
# ============================================================

@login_required(login_url="/student/login/")
def enroll_course(request, slug):

    course = get_object_or_404(
        Course,
        slug=slug,
        is_active=True
    )

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            "is_active": False
        }
    )

    if created:
        messages.success(
            request,
            (
                f"Enrollment request for {course.title} has been submitted. "
                "Please complete the payment and wait for admin confirmation."
            )
        )
    elif enrollment.is_active:
        messages.info(
            request,
            f"You already have active access to {course.title}."
        )
    else:
        messages.info(
            request,
            (
                f"Your enrollment for {course.title} is waiting for "
                "payment confirmation."
            )
        )

    return redirect(
        "student_dashboard"
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@login_required(login_url="/student/login/")
def student_dashboard(request):

    enrollments = list(
        Enrollment.objects
        .filter(
            user=request.user,
            is_active=True
        )
        .select_related("course")
    )

    for enrollment in enrollments:

        course = enrollment.course

        total_lessons = Lesson.objects.filter(
            course=course,
            is_active=True
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            lesson__is_active=True,
            completed=True
        ).count()

        if total_lessons > 0:

            progress_percentage = round(
                (completed_lessons / total_lessons) * 100
            )

        else:

            progress_percentage = 0

        enrollment.total_lessons = total_lessons

        enrollment.completed_lessons = completed_lessons

        enrollment.progress_percentage = (
            progress_percentage
        )

        enrollment.is_completed = (
            total_lessons > 0
            and completed_lessons >= total_lessons
        )

        enrollment.certificate = (
            get_or_create_course_certificate(
                request.user,
                course
            )
        )

    return render(
        request,
        "lms/student_dashboard.html",
        {
            "enrollments": enrollments
        }
    )


# ============================================================
# COURSE LEARNING PAGE
# ============================================================

@login_required(login_url="/student/login/")
def course_learning(request, slug):

    course = get_object_or_404(
        Course,
        slug=slug,
        is_active=True
    )

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course,
        is_active=True
    )

    lessons = list(
        Lesson.objects.filter(
            course=course,
            is_active=True
        ).order_by(
            "lesson_number",
            "id"
        )
    )

    completed_lesson_ids = set(
        LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            lesson__is_active=True,
            completed=True
        ).values_list(
            "lesson_id",
            flat=True
        )
    )

    for lesson in lessons:

        lesson.is_completed = (
            lesson.id in completed_lesson_ids
        )

    total_lessons = len(lessons)

    completed_lessons = len(
        completed_lesson_ids
    )

    if total_lessons > 0:

        progress_percentage = round(
            (completed_lessons / total_lessons) * 100
        )

    else:

        progress_percentage = 0

    next_lesson = None

    for lesson in lessons:

        if not lesson.is_completed:

            next_lesson = lesson

            break

    course_completed = (
        total_lessons > 0
        and completed_lessons >= total_lessons
    )

    certificate = None

    if course_completed:

        certificate = (
            get_or_create_course_certificate(
                request.user,
                course
            )
        )

    else:

        certificate = Certificate.objects.filter(
            user=request.user,
            course=course
        ).first()

    return render(
        request,
        "lms/course_learning.html",
        {
            "course": course,
            "enrollment": enrollment,
            "lessons": lessons,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "next_lesson": next_lesson,
            "course_completed": course_completed,
            "certificate": certificate,
        }
    )


# ============================================================
# LESSON DETAIL
# ============================================================

@login_required(login_url="/student/login/")
def lesson_detail(request, slug, lesson_id):

    course = get_object_or_404(
        Course,
        slug=slug,
        is_active=True
    )

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course,
        is_active=True
    )

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        course=course,
        is_active=True
    )

    # --------------------------------------------------------
    # MARK LESSON COMPLETE
    # --------------------------------------------------------

    if request.method == "POST":

        progress, created = (
            LessonProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )
        )

        progress.completed = True

        progress.completed_at = timezone.now()

        progress.save()

        messages.success(
            request,
            f"Lesson {lesson.lesson_number} completed!"
        )

        total_lessons = Lesson.objects.filter(
            course=course,
            is_active=True
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            lesson__is_active=True,
            completed=True
        ).count()

        if (
            total_lessons > 0
            and completed_lessons >= total_lessons
        ):

            certificate = (
                get_or_create_course_certificate(
                    request.user,
                    course
                )
            )

            if certificate:

                messages.success(
                    request,
                    "🎉 Congratulations! Your course certificate is ready."
                )

        return redirect(
            "lesson_detail",
            slug=course.slug,
            lesson_id=lesson.id
        )

    # --------------------------------------------------------
    # CURRENT LESSON PROGRESS
    # --------------------------------------------------------

    lesson_progress = LessonProgress.objects.filter(
        user=request.user,
        lesson=lesson
    ).first()

    is_completed = (
        lesson_progress.completed
        if lesson_progress
        else False
    )

    # --------------------------------------------------------
    # ALL ACTIVE LESSONS
    # --------------------------------------------------------

    lessons = list(
        Lesson.objects.filter(
            course=course,
            is_active=True
        ).order_by(
            "lesson_number",
            "id"
        )
    )

    # --------------------------------------------------------
    # FIND CURRENT LESSON
    # --------------------------------------------------------

    current_index = None

    for index, item in enumerate(lessons):

        if item.id == lesson.id:

            current_index = index

            break

    # --------------------------------------------------------
    # PREVIOUS LESSON
    # --------------------------------------------------------

    previous_lesson = None

    if (
        current_index is not None
        and current_index > 0
    ):

        previous_lesson = lessons[
            current_index - 1
        ]

    # --------------------------------------------------------
    # NEXT LESSON
    # --------------------------------------------------------

    next_lesson = None

    if (
        current_index is not None
        and current_index < len(lessons) - 1
    ):

        next_lesson = lessons[
            current_index + 1
        ]

    # --------------------------------------------------------
    # COURSE PROGRESS
    # --------------------------------------------------------

    total_lessons = len(lessons)

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        lesson__is_active=True,
        completed=True
    ).count()

    if total_lessons > 0:

        progress_percentage = round(
            (completed_lessons / total_lessons) * 100
        )

    else:

        progress_percentage = 0

    # --------------------------------------------------------
    # COURSE COMPLETED
    # --------------------------------------------------------

    course_completed = (
        total_lessons > 0
        and completed_lessons >= total_lessons
    )

    # --------------------------------------------------------
    # CERTIFICATE
    # --------------------------------------------------------

    certificate = None

    if course_completed:

        certificate = (
            get_or_create_course_certificate(
                request.user,
                course
            )
        )

    else:

        certificate = Certificate.objects.filter(
            user=request.user,
            course=course
        ).first()

    return render(
        request,
        "lms/lesson_detail.html",
        {
            "course": course,
            "enrollment": enrollment,
            "lesson": lesson,
            "lesson_progress": lesson_progress,
            "is_completed": is_completed,
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "course_completed": course_completed,
            "certificate": certificate,
        }
    )


# ============================================================
# CERTIFICATE DETAIL
# ============================================================

@login_required(login_url="/student/login/")
def certificate_detail(request, certificate_id):

    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        user=request.user
    )

    return render(
        request,
        "lms/certificate.html",
        {
            "certificate": certificate,
            "student": request.user,
            "course": certificate.course,
        }
    )


# ============================================================
# STUDENT REGISTRATION
# ============================================================

def student_register(request):

    if request.user.is_authenticated:

        return redirect(
            "student_dashboard"
        )

    if request.method == "POST":

        form = StudentRegistrationForm(
            request.POST
        )

        if form.is_valid():

            try:

                with transaction.atomic():

                    user = User.objects.create_user(
                        username=form.cleaned_data[
                            "username"
                        ],
                        first_name=form.cleaned_data[
                            "first_name"
                        ],
                        last_name=form.cleaned_data[
                            "last_name"
                        ],
                        email=form.cleaned_data[
                            "email"
                        ],
                        password=form.cleaned_data[
                            "password"
                        ]
                    )

                    StudentProfile.objects.create(
                        user=user,
                        phone=form.cleaned_data[
                            "phone"
                        ],
                        qualification=form.cleaned_data[
                            "qualification"
                        ],
                        college_company=form.cleaned_data[
                            "college_company"
                        ]
                    )

                messages.success(
                    request,
                    "Registration successful! You can now login."
                )

                return redirect(
                    "student_login"
                )

            except Exception as e:

                messages.error(
                    request,
                    f"Registration failed: {e}"
                )

    else:

        form = StudentRegistrationForm()

    return render(
        request,
        "lms/student_register.html",
        {
            "form": form
        }
    )



# ============================================================
# STUDENT - PROFILE HELPER
# ============================================================

def get_or_create_student_profile(user):
    """Return the student's profile and safely create it if missing."""

    profile = StudentProfile.objects.filter(
        user=user
    ).first()

    if profile:
        return profile

    temporary_phone = f"TEMP{user.pk}"[:15]

    profile = StudentProfile.objects.create(
        user=user,
        phone=temporary_phone,
        qualification="Other",
        college_company="",
    )

    return profile


# ============================================================
# STUDENT - PROFILE
# ============================================================

@login_required(login_url="/student/login/")
def student_profile(request):

    profile = get_or_create_student_profile(
        request.user
    )

    return render(
        request,
        "lms/student_profile.html",
        {
            "profile": profile,
            "student": request.user,
        }
    )


# ============================================================
# STUDENT - EDIT PROFILE
# ============================================================

@login_required(login_url="/student/login/")
def student_profile_edit(request):

    profile = get_or_create_student_profile(
        request.user
    )

    if request.method == "POST":

        first_name = request.POST.get(
            "first_name", ""
        ).strip()
        last_name = request.POST.get(
            "last_name", ""
        ).strip()
        email = request.POST.get(
            "email", ""
        ).strip()
        phone = request.POST.get(
            "phone", ""
        ).strip()
        qualification = request.POST.get(
            "qualification", ""
        ).strip()
        college_company = request.POST.get(
            "college_company", ""
        ).strip()

        valid_qualifications = {
            value
            for value, label
            in StudentProfile.QUALIFICATION_CHOICES
        }

        if not first_name:
            messages.error(
                request,
                "First name is required."
            )
        elif not email:
            messages.error(
                request,
                "Email address is required."
            )
        elif not phone:
            messages.error(
                request,
                "Phone number is required."
            )
        elif len(phone) > 15:
            messages.error(
                request,
                "Phone number cannot exceed 15 characters."
            )
        elif qualification not in valid_qualifications:
            messages.error(
                request,
                "Please select a valid qualification."
            )
        elif (
            User.objects
            .filter(email__iexact=email)
            .exclude(id=request.user.id)
            .exists()
        ):
            messages.error(
                request,
                "This email address is already being used."
            )
        elif (
            StudentProfile.objects
            .filter(phone=phone)
            .exclude(user=request.user)
            .exists()
        ):
            messages.error(
                request,
                "This phone number is already registered."
            )
        else:
            with transaction.atomic():
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save(
                    update_fields=[
                        "first_name",
                        "last_name",
                        "email",
                    ]
                )

                profile.phone = phone
                profile.qualification = qualification
                profile.college_company = college_company
                profile.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("student_profile")

    return render(
        request,
        "lms/student_profile_edit.html",
        {
            "profile": profile,
            "student": request.user,
        }
    )


# ============================================================
# STUDENT - CHANGE PASSWORD
# ============================================================

@login_required(login_url="/student/login/")
def student_change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("student_profile")

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "lms/student_change_password.html",
        {
            "form": form,
        }
    )



# ============================================================
# ADMIN PERMISSION HELPER
# ============================================================

def is_admin_user(user):

    return (
        user.is_authenticated
        and user.is_staff
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_dashboard(request):

    total_students = StudentProfile.objects.count()

    total_courses = Course.objects.filter(
        is_active=True
    ).count()

    total_enrollments = Enrollment.objects.filter(
        is_active=True
    ).count()

    total_certificates = Certificate.objects.count()

    recent_enrollments = (
        Enrollment.objects
        .select_related(
            "user",
            "course"
        )
        .order_by(
            "-enrolled_at"
        )[:5]
    )

    recent_certificates = (
        Certificate.objects
        .select_related(
            "user",
            "course"
        )
        .order_by(
            "-issued_at"
        )[:5]
    )

    recent_courses = Course.objects.order_by(
        "-created_at"
    )[:5]

    context = {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_certificates": total_certificates,
        "recent_enrollments": recent_enrollments,
        "recent_certificates": recent_certificates,
        "recent_courses": recent_courses,
    }

    return render(
        request,
        "lms/admin_dashboard.html",
        context
    )


# ============================================================
# ADMIN - STUDENT MANAGEMENT
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_student_management(request):

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    students = (
        StudentProfile.objects
        .select_related("user")
        .order_by("-created_at")
    )

    if search_query:

        students = students.filter(
            Q(
                user__username__icontains=search_query
            )
            |
            Q(
                user__first_name__icontains=search_query
            )
            |
            Q(
                user__last_name__icontains=search_query
            )
            |
            Q(
                user__email__icontains=search_query
            )
            |
            Q(
                phone__icontains=search_query
            )
            |
            Q(
                qualification__icontains=search_query
            )
            |
            Q(
                college_company__icontains=search_query
            )
        )

    total_students = StudentProfile.objects.count()

    active_students = StudentProfile.objects.filter(
        user__is_active=True
    ).count()

    inactive_students = StudentProfile.objects.filter(
        user__is_active=False
    ).count()

    context = {
        "students": students,
        "search_query": search_query,
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,
    }

    return render(
        request,
        "lms/admin_students.html",
        context
    )


# ============================================================
# ADMIN - STUDENT DETAIL
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_student_detail(request, student_id):

    student = get_object_or_404(
        StudentProfile.objects.select_related("user"),
        id=student_id
    )

    enrollments = (
        Enrollment.objects
        .filter(
            user=student.user
        )
        .select_related("course")
        .order_by("-enrolled_at")
    )

    certificates = (
        Certificate.objects
        .filter(
            user=student.user
        )
        .select_related("course")
        .order_by("-issued_at")
    )

    context = {
        "student": student,
        "enrollments": enrollments,
        "certificates": certificates,
    }

    return render(
        request,
        "lms/admin_student_detail.html",
        context
    )


# ============================================================
# ADMIN - COURSE MANAGEMENT
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_course_management(request):

    courses = Course.objects.all().order_by(
        "-created_at"
    )

    active_courses = Course.objects.filter(
        is_active=True
    ).count()

    inactive_courses = Course.objects.filter(
        is_active=False
    ).count()

    context = {
        "courses": courses,
        "active_courses": active_courses,
        "inactive_courses": inactive_courses,
    }

    return render(
        request,
        "lms/admin_courses.html",
        context
    )


# ============================================================
# ADMIN - ADD COURSE
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_course_add(request):

    if request.method == "POST":

        form = CourseAdminForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            course = form.save()

            messages.success(
                request,
                f'Course "{course.title}" created successfully.'
            )

            return redirect(
                "admin_course_management"
            )

    else:

        form = CourseAdminForm()

    context = {
        "form": form,
        "page_title": "Add Course",
        "button_text": "Create Course",
    }

    return render(
        request,
        "lms/admin_course_form.html",
        context
    )


# ============================================================
# ADMIN - EDIT COURSE
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_course_edit(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        form = CourseAdminForm(
            request.POST,
            request.FILES,
            instance=course
        )

        if form.is_valid():

            course = form.save()

            messages.success(
                request,
                f'Course "{course.title}" updated successfully.'
            )

            return redirect(
                "admin_course_management"
            )

    else:

        form = CourseAdminForm(
            instance=course
        )

    context = {
        "form": form,
        "course": course,
        "page_title": "Edit Course",
        "button_text": "Update Course",
    }

    return render(
        request,
        "lms/admin_course_form.html",
        context
    )


# ============================================================
# ADMIN - ACTIVATE / DEACTIVATE COURSE
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_course_toggle(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    course.is_active = not course.is_active

    course.save(
        update_fields=[
            "is_active",
            "updated_at"
        ]
    )

    if course.is_active:

        messages.success(
            request,
            f'"{course.title}" has been activated.'
        )

    else:

        messages.warning(
            request,
            f'"{course.title}" has been deactivated.'
        )

    return redirect(
        "admin_course_management"
    )


# ============================================================
# ADMIN - DELETE COURSE
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_course_delete(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    course_title = course.title

    if request.method == "POST":

        course.delete()

        messages.success(
            request,
            f'Course "{course_title}" deleted successfully.'
        )

        return redirect(
            "admin_course_management"
        )

    return render(
        request,
        "lms/admin_course_delete.html",
        {
            "course": course
        }
    )


# ============================================================
# ADMIN - LESSON MANAGEMENT
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_lesson_management(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    lessons = Lesson.objects.filter(
        course=course
    ).order_by(
        "lesson_number",
        "id"
    )

    context = {
        "course": course,
        "lessons": lessons,
    }

    return render(
        request,
        "lms/admin_lesson_management.html",
        context
    )


# ============================================================
# ADMIN - ADD LESSON
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_lesson_add(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        form = LessonAdminForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            lesson_number = form.cleaned_data[
                "lesson_number"
            ]

            duplicate = Lesson.objects.filter(
                course=course,
                lesson_number=lesson_number
            ).exists()

            if duplicate:

                form.add_error(
                    "lesson_number",
                    (
                        f"Lesson number {lesson_number} "
                        f"already exists for this course."
                    )
                )

            else:

                lesson = form.save(
                    commit=False
                )

                lesson.course = course

                lesson.save()

                messages.success(
                    request,
                    (
                        f'Lesson "{lesson.title}" '
                        f'created successfully.'
                    )
                )

                return redirect(
                    "admin_lesson_management",
                    course_id=course.id
                )

    else:

        last_lesson = (
            Lesson.objects
            .filter(course=course)
            .order_by("-lesson_number")
            .first()
        )

        next_lesson_number = (
            last_lesson.lesson_number + 1
            if last_lesson
            else 1
        )

        form = LessonAdminForm(
            initial={
                "lesson_number": next_lesson_number,
                "is_active": True,
            }
        )

    context = {
        "course": course,
        "form": form,
        "page_title": "Add Lesson",
        "button_text": "Create Lesson",
    }

    return render(
        request,
        "lms/admin_lesson_form.html",
        context
    )


# ============================================================
# ADMIN - EDIT LESSON
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_lesson_edit(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    course = lesson.course

    if request.method == "POST":

        form = LessonAdminForm(
            request.POST,
            request.FILES,
            instance=lesson
        )

        if form.is_valid():

            lesson_number = form.cleaned_data[
                "lesson_number"
            ]

            duplicate = (
                Lesson.objects
                .filter(
                    course=course,
                    lesson_number=lesson_number
                )
                .exclude(
                    id=lesson.id
                )
                .exists()
            )

            if duplicate:

                form.add_error(
                    "lesson_number",
                    (
                        f"Lesson number {lesson_number} "
                        f"already exists for this course."
                    )
                )

            else:

                lesson = form.save()

                messages.success(
                    request,
                    (
                        f'Lesson "{lesson.title}" '
                        f'updated successfully.'
                    )
                )

                return redirect(
                    "admin_lesson_management",
                    course_id=course.id
                )

    else:

        form = LessonAdminForm(
            instance=lesson
        )

    context = {
        "course": course,
        "lesson": lesson,
        "form": form,
        "page_title": "Edit Lesson",
        "button_text": "Update Lesson",
    }

    return render(
        request,
        "lms/admin_lesson_form.html",
        context
    )


# ============================================================
# ADMIN - ACTIVATE / DEACTIVATE LESSON
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_lesson_toggle(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    lesson.is_active = not lesson.is_active

    lesson.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if lesson.is_active:

        messages.success(
            request,
            f'"{lesson.title}" has been activated.'
        )

    else:

        messages.warning(
            request,
            f'"{lesson.title}" has been deactivated.'
        )

    return redirect(
        "admin_lesson_management",
        course_id=lesson.course.id
    )


# ============================================================
# ADMIN - DELETE LESSON
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_lesson_delete(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    course = lesson.course

    lesson_title = lesson.title

    if request.method == "POST":

        lesson.delete()

        messages.success(
            request,
            f'Lesson "{lesson_title}" deleted successfully.'
        )

        return redirect(
            "admin_lesson_management",
            course_id=course.id
        )

    return render(
        request,
        "lms/admin_lesson_delete.html",
        {
            "course": course,
            "lesson": lesson,
        }
    )

# ============================================================
# ADMIN - BATCH MANAGEMENT
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_batch_management(request):

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    batches = (
        Batch.objects
        .select_related("course")
        .order_by("-created_at")
    )

    if search_query:

        batches = batches.filter(

            Q(
                name__icontains=search_query
            )

            |

            Q(
                batch_code__icontains=search_query
            )

            |

            Q(
                course__title__icontains=search_query
            )

            |

            Q(
                instructor__icontains=search_query
            )

            |

            Q(
                schedule__icontains=search_query
            )
        )

    total_batches = Batch.objects.count()

    upcoming_batches = Batch.objects.filter(
        status="upcoming"
    ).count()

    active_batches = Batch.objects.filter(
        status="active"
    ).count()

    completed_batches = Batch.objects.filter(
        status="completed"
    ).count()

    cancelled_batches = Batch.objects.filter(
        status="cancelled"
    ).count()

    context = {

        "batches": batches,

        "search_query": search_query,

        "total_batches": total_batches,

        "upcoming_batches": upcoming_batches,

        "active_batches": active_batches,

        "completed_batches": completed_batches,

        "cancelled_batches": cancelled_batches,
    }

    return render(
        request,
        "lms/admin_batches.html",
        context
    )


# ============================================================
# ADMIN - ADD BATCH
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_batch_add(request):

    if request.method == "POST":

        form = BatchAdminForm(
            request.POST
        )

        if form.is_valid():

            batch = form.save()

            messages.success(
                request,
                (
                    f'Batch "{batch.name}" '
                    f'created successfully.'
                )
            )

            return redirect(
                "admin_batch_management"
            )

    else:

        form = BatchAdminForm(
            initial={
                "instructor": (
                    "Kameera Technologies"
                ),

                "maximum_students": 30,

                "status": "upcoming",
            }
        )

    context = {

        "form": form,

        "page_title": "Add Batch",

        "button_text": "Create Batch",
    }

    return render(
        request,
        "lms/admin_batch_form.html",
        context
    )


# ============================================================
# ADMIN - EDIT BATCH
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_batch_edit(
    request,
    batch_id
):

    batch = get_object_or_404(
        Batch,
        id=batch_id
    )

    if request.method == "POST":

        form = BatchAdminForm(
            request.POST,
            instance=batch
        )

        if form.is_valid():

            batch = form.save()

            messages.success(
                request,
                (
                    f'Batch "{batch.name}" '
                    f'updated successfully.'
                )
            )

            return redirect(
                "admin_batch_management"
            )

    else:

        form = BatchAdminForm(
            instance=batch
        )

    context = {

        "form": form,

        "batch": batch,

        "page_title": "Edit Batch",

        "button_text": "Update Batch",
    }

    return render(
        request,
        "lms/admin_batch_form.html",
        context
    )


# ============================================================
# ADMIN - ACTIVATE / DEACTIVATE BATCH
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_batch_toggle(
    request,
    batch_id
):

    batch = get_object_or_404(
        Batch,
        id=batch_id
    )

    if batch.status == "active":

        batch.status = "upcoming"

        messages.warning(
            request,
            (
                f'Batch "{batch.name}" '
                f'has been deactivated.'
            )
        )

    else:

        batch.status = "active"

        messages.success(
            request,
            (
                f'Batch "{batch.name}" '
                f'has been activated.'
            )
        )

    batch.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return redirect(
        "admin_batch_management"
    )


# ============================================================
# ADMIN - DELETE BATCH
# ============================================================

@login_required(login_url="/admin/login/")
@user_passes_test(is_admin_user)
def admin_batch_delete(
    request,
    batch_id
):

    batch = get_object_or_404(
        Batch,
        id=batch_id
    )

    batch_name = batch.name

    if request.method == "POST":

        batch.delete()

        messages.success(
            request,
            (
                f'Batch "{batch_name}" '
                f'deleted successfully.'
            )
        )

        return redirect(
            "admin_batch_management"
        )

    return render(
        request,
        "lms/admin_batch_delete.html",
        {
            "batch": batch
        }
    )
# ============================================================
# ADMIN - FEE MANAGEMENT
# ============================================================

@login_required
@user_passes_test(is_admin_user)
def admin_fee_management(request):

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    fees = (
        StudentFee.objects
        .select_related(
            "student",
            "course"
        )
        .order_by(
            "-created_at"
        )
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search_query:

        fees = fees.filter(
            Q(
                student__username__icontains=
                search_query
            )
            |
            Q(
                student__first_name__icontains=
                search_query
            )
            |
            Q(
                student__last_name__icontains=
                search_query
            )
            |
            Q(
                student__email__icontains=
                search_query
            )
            |
            Q(
                course__title__icontains=
                search_query
            )
        )

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    if status_filter in [
        "Pending",
        "Partial",
        "Paid",
    ]:

        fees = fees.filter(
            payment_status=status_filter
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    fee_summary = StudentFee.objects.aggregate(
        total_fee=Sum("course_fee"),
        total_discount=Sum("discount"),
        total_paid=Sum("paid_amount"),
        total_pending=Sum("pending_amount"),
    )

    total_fee = (
        fee_summary["total_fee"] or 0
    )

    total_discount = (
        fee_summary["total_discount"] or 0
    )

    total_paid = (
        fee_summary["total_paid"] or 0
    )

    total_pending = (
        fee_summary["total_pending"] or 0
    )

    total_records = StudentFee.objects.count()

    pending_count = StudentFee.objects.filter(
        payment_status="Pending"
    ).count()

    partial_count = StudentFee.objects.filter(
        payment_status="Partial"
    ).count()

    paid_count = StudentFee.objects.filter(
        payment_status="Paid"
    ).count()

    context = {
        "fees": fees,

        "search_query": search_query,

        "status_filter": status_filter,

        "total_fee": total_fee,

        "total_discount": total_discount,

        "total_paid": total_paid,

        "total_pending": total_pending,

        "total_records": total_records,

        "pending_count": pending_count,

        "partial_count": partial_count,

        "paid_count": paid_count,
    }

    return render(
        request,
        "lms/admin_fees.html",
        context
    )
# ============================================================
# ADMIN - ADD STUDENT FEE
# ============================================================

@login_required
@user_passes_test(is_admin_user)
def admin_fee_add(request):

    if request.method == "POST":

        form = StudentFeeAdminForm(
            request.POST
        )

        if form.is_valid():

            fee = form.save()

            messages.success(
                request,
                "Student fee record created successfully."
            )

            return redirect(
                "admin_fee_management"
            )

    else:

        form = StudentFeeAdminForm()

    context = {
        "form": form,
        "page_title": "Add Student Fee",
        "button_text": "Create Fee Record",
    }

    return render(
        request,
        "lms/admin_fee_form.html",
        context
    )
# ============================================================
# ADMIN - FEE DETAIL
# ============================================================

@login_required
@user_passes_test(is_admin_user)
def admin_fee_detail(request, fee_id):

    fee = get_object_or_404(
        StudentFee.objects.select_related(
            "student",
            "course"
        ),
        id=fee_id
    )

    payments = (
        Payment.objects
        .filter(
            student_fee=fee
        )
        .order_by(
            "-payment_date",
            "-created_at"
        )
    )

    enrollment = (
        Enrollment.objects
        .filter(
            user=fee.student,
            course=fee.course
        )
        .first()
    )

    context = {
        "fee": fee,
        "payments": payments,
        "enrollment": enrollment,
    }

    return render(
        request,
        "lms/admin_fee_detail.html",
        context
    )


# ============================================================
# ADMIN - ADD PAYMENT
# ============================================================

@login_required
@user_passes_test(is_admin_user)
def admin_payment_add(
    request,
    fee_id
):

    fee = get_object_or_404(
        StudentFee,
        id=fee_id
    )

    if fee.balance <= 0:

        messages.info(
            request,
            "This fee is already fully paid."
        )

        return redirect(
            "admin_fee_detail",
            fee_id=fee.id
        )

    if request.method == "POST":

        form = PaymentAdminForm(
            request.POST,
            student_fee=fee
        )

        if form.is_valid():

            try:

                with transaction.atomic():

                    payment = form.save(
                        commit=False
                    )

                    payment.student_fee = fee

                    payment.save()

                    total_paid = (
                        Payment.objects
                        .filter(
                            student_fee=fee
                        )
                        .aggregate(
                            total=Sum("amount")
                        )["total"]
                        or 0
                    )

                    fee.paid_amount = total_paid

                    fee.last_payment_date = (
                        payment.payment_date
                    )

                    fee.save()

                messages.success(
                    request,
                    f"Payment of ₹{payment.amount} "
                    f"recorded successfully."
                )

                return redirect(
                    "admin_fee_detail",
                    fee_id=fee.id
                )

            except Exception as e:

                messages.error(
                    request,
                    f"Payment failed: {e}"
                )

    else:

        form = PaymentAdminForm(
            student_fee=fee
        )

    context = {
        "form": form,
        "fee": fee,
        "page_title": "Record Payment",
        "button_text": "Save Payment",
    }

    return render(
        request,
        "lms/admin_payment_form.html",
        context
    )


# ============================================================
# ADMIN - ACTIVATE ENROLLMENT
# ============================================================

@login_required
@user_passes_test(is_admin_user)
def admin_activate_enrollment(request, fee_id):

    fee = get_object_or_404(
        StudentFee.objects.select_related(
            "student",
            "course"
        ),
        id=fee_id
    )

    if fee.balance > 0:
        messages.error(
            request,
            (
                "Enrollment cannot be activated because "
                f"₹{fee.balance} is still pending."
            )
        )
        return redirect(
            "admin_fee_detail",
            fee_id=fee.id
        )

    enrollment, created = Enrollment.objects.get_or_create(
        user=fee.student,
        course=fee.course,
        defaults={"is_active": False}
    )

    if enrollment.is_active:
        messages.info(
            request,
            f"Enrollment for {fee.student.username} is already active."
        )
    else:
        enrollment.is_active = True
        enrollment.save(update_fields=["is_active"])
        messages.success(
            request,
            (
                f"Enrollment for {fee.student.username} in "
                f"{fee.course.title} has been activated successfully."
            )
        )

    return redirect(
        "admin_fee_detail",
        fee_id=fee.id
    )


# ============================================================
# ADMIN - DEACTIVATE ENROLLMENT
# ============================================================

@login_required
@user_passes_test(is_admin_user)
def admin_deactivate_enrollment(request, fee_id):

    fee = get_object_or_404(
        StudentFee.objects.select_related(
            "student",
            "course"
        ),
        id=fee_id
    )

    enrollment = get_object_or_404(
        Enrollment,
        user=fee.student,
        course=fee.course
    )

    enrollment.is_active = False
    enrollment.save(update_fields=["is_active"])

    messages.warning(
        request,
        (
            f"Enrollment for {fee.student.username} in "
            f"{fee.course.title} has been deactivated."
        )
    )

    return redirect(
        "admin_fee_detail",
        fee_id=fee.id
    )
