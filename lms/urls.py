from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # ============================================================
    # HOME
    # ============================================================

    path(
        "",
        views.home,
        name="home"
    ),


    # ============================================================
    # COURSES
    # ============================================================

    path(
        "courses/",
        views.course_list,
        name="course_list"
    ),

    path(
        "courses/<slug:slug>/",
        views.course_detail,
        name="course_detail"
    ),

    path(
        "courses/<slug:slug>/enroll/",
        views.enroll_course,
        name="enroll_course"
    ),


    # ============================================================
    # STUDENT REGISTRATION
    # ============================================================

    path(
        "student/register/",
        views.student_register,
        name="student_register"
    ),


    # ============================================================
    # STUDENT LOGIN
    # ============================================================

    path(
        "student/login/",
        auth_views.LoginView.as_view(
            template_name="lms/student_login.html",
            redirect_authenticated_user=True,
            next_page="student_dashboard"
        ),
        name="student_login"
    ),


    # ============================================================
    # STUDENT LOGOUT
    # ============================================================

    path(
        "student/logout/",
        auth_views.LogoutView.as_view(
            next_page="home"
        ),
        name="logout"
    ),


    # ============================================================
    # FORGOT PASSWORD
    # ============================================================

    path(
        "student/password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="lms/password_reset.html",
            email_template_name="lms/password_reset_email.html",
            subject_template_name="lms/password_reset_subject.txt",
            success_url="/student/password-reset/done/"
        ),
        name="password_reset"
    ),

    path(
        "student/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="lms/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
        "student/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="lms/password_reset_confirm.html",
            success_url="/student/reset/done/"
        ),
        name="password_reset_confirm"
    ),

    path(
        "student/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="lms/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),


    # ============================================================
    # STUDENT PROFILE
    # ============================================================

    path(
        "student/profile/",
        views.student_profile,
        name="student_profile"
    ),

    path(
        "student/profile/edit/",
        views.student_profile_edit,
        name="student_profile_edit"
    ),

    path(
        "student/change-password/",
        views.student_change_password,
        name="student_change_password"
    ),


    # ============================================================
    # STUDENT DASHBOARD
    # ============================================================

    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),


    # ============================================================
    # COURSE LEARNING
    # ============================================================

    path(
        "student/course/<slug:slug>/",
        views.course_learning,
        name="course_learning"
    ),

    path(
        "student/course/<slug:slug>/lesson/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail"
    ),


    # ============================================================
    # CERTIFICATE
    # ============================================================

    path(
        "student/certificate/<str:certificate_id>/",
        views.certificate_detail,
        name="certificate_detail"
    ),


    # ============================================================
    # ADMIN DASHBOARD
    # ============================================================

    path(
        "admin/dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # ============================================================
    # ADMIN - STUDENT MANAGEMENT
    # ============================================================

    path(
        "admin/dashboard/students/",
        views.admin_student_management,
        name="admin_student_management"
    ),

    path(
        "admin/dashboard/students/<int:student_id>/",
        views.admin_student_detail,
        name="admin_student_detail"
    ),


    # ============================================================
    # ADMIN - COURSE MANAGEMENT
    # ============================================================

    path(
        "admin/dashboard/courses/",
        views.admin_course_management,
        name="admin_course_management"
    ),

    path(
        "admin/dashboard/courses/add/",
        views.admin_course_add,
        name="admin_course_add"
    ),

    path(
        "admin/dashboard/courses/<int:course_id>/edit/",
        views.admin_course_edit,
        name="admin_course_edit"
    ),

    path(
        "admin/dashboard/courses/<int:course_id>/toggle/",
        views.admin_course_toggle,
        name="admin_course_toggle"
    ),

    path(
        "admin/dashboard/courses/<int:course_id>/delete/",
        views.admin_course_delete,
        name="admin_course_delete"
    ),


    # ============================================================
    # ADMIN - LESSON MANAGEMENT
    # ============================================================

    path(
        "admin/dashboard/courses/<int:course_id>/lessons/",
        views.admin_lesson_management,
        name="admin_lesson_management"
    ),

    path(
        "admin/dashboard/courses/<int:course_id>/lessons/add/",
        views.admin_lesson_add,
        name="admin_lesson_add"
    ),

    path(
        "admin/dashboard/lessons/<int:lesson_id>/edit/",
        views.admin_lesson_edit,
        name="admin_lesson_edit"
    ),

    path(
        "admin/dashboard/lessons/<int:lesson_id>/toggle/",
        views.admin_lesson_toggle,
        name="admin_lesson_toggle"
    ),

    path(
        "admin/dashboard/lessons/<int:lesson_id>/delete/",
        views.admin_lesson_delete,
        name="admin_lesson_delete"
    ),


    # ============================================================
    # ADMIN - BATCH MANAGEMENT
    # ============================================================

    path(
        "admin/dashboard/batches/",
        views.admin_batch_management,
        name="admin_batch_management"
    ),

    path(
        "admin/dashboard/batches/add/",
        views.admin_batch_add,
        name="admin_batch_add"
    ),

    path(
        "admin/dashboard/batches/<int:batch_id>/edit/",
        views.admin_batch_edit,
        name="admin_batch_edit"
    ),

    path(
        "admin/dashboard/batches/<int:batch_id>/toggle/",
        views.admin_batch_toggle,
        name="admin_batch_toggle"
    ),

    path(
        "admin/dashboard/batches/<int:batch_id>/delete/",
        views.admin_batch_delete,
        name="admin_batch_delete"
    ),


    # ============================================================
    # ADMIN - FEE MANAGEMENT
    # ============================================================

    path(
        "admin/dashboard/fees/",
        views.admin_fee_management,
        name="admin_fee_management"
    ),

    path(
        "admin/dashboard/fees/add/",
        views.admin_fee_add,
        name="admin_fee_add"
    ),

    path(
        "admin/dashboard/fees/<int:fee_id>/",
        views.admin_fee_detail,
        name="admin_fee_detail"
    ),

    path(
        "admin/dashboard/fees/<int:fee_id>/payment/add/",
        views.admin_payment_add,
        name="admin_payment_add"
    ),


    # ============================================================
    # ADMIN - ACTIVATE ENROLLMENT
    # ============================================================

    path(
        "admin/dashboard/fees/<int:fee_id>/activate-enrollment/",
        views.admin_activate_enrollment,
        name="admin_activate_enrollment"
    ),


    # ============================================================
    # ADMIN - DEACTIVATE ENROLLMENT
    # ============================================================

    path(
        "admin/dashboard/fees/<int:fee_id>/deactivate-enrollment/",
        views.admin_deactivate_enrollment,
        name="admin_deactivate_enrollment"
    ),

]