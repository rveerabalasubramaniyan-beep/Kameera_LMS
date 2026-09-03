from django.contrib import admin

from .models import (
    Course,
    Enrollment,
    StudentProfile,
    Lesson,
    LessonProgress,
)


# ============================================================
# COURSE ADMIN
# ============================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "level",
        "price",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "level",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
        "short_description",
        "instructor",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    ordering = (
        "-created_at",
    )


# ============================================================
# ENROLLMENT ADMIN
# ============================================================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "course",
        "enrolled_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "course",
    )

    search_fields = (
        "user__username",
        "user__email",
        "course__title",
    )

    ordering = (
        "-enrolled_at",
    )


# ============================================================
# STUDENT PROFILE ADMIN
# ============================================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "qualification",
        "college_company",
        "created_at",
    )

    list_filter = (
        "qualification",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
        "college_company",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# LESSON ADMIN
# ============================================================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "lesson_number",
        "title",
        "is_active",
        "created_at",
    )

    list_filter = (
        "course",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
        "course__title",
    )

    ordering = (
        "course",
        "lesson_number",
    )


# ============================================================
# LESSON PROGRESS ADMIN
# ============================================================

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "lesson",
        "course_name",
        "completed",
        "updated_at",
    )

    list_filter = (
        "completed",
        "lesson__course",
    )

    search_fields = (
        "user__username",
        "user__email",
        "lesson__title",
        "lesson__course__title",
    )

    readonly_fields = (
        "completed",
        "updated_at",
    )

    ordering = (
        "lesson__course",
        "lesson__lesson_number",
    )

    @admin.display(description="Course")
    def course_name(self, obj):
        return obj.lesson.course.title