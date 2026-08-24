from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User


ZERO_DECIMAL = Decimal("0.00")


# ============================================================
# COURSE
# ============================================================

class Course(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    short_description = models.CharField(
        max_length=300
    )

    description = models.TextField()

    category = models.CharField(
        max_length=100,
        default="Data Analytics"
    )

    duration = models.CharField(
        max_length=100,
        default="8 Weeks"
    )

    level = models.CharField(
        max_length=50,
        default="Beginner"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    instructor = models.CharField(
        max_length=150,
        default="Kameera Technologies"
    )

    image = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return self.title


# ============================================================
# ENROLLMENT
# ============================================================

class Enrollment(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # New enrollments are INACTIVE.
    # Admin activates the enrollment after payment
    # confirmation.
    # --------------------------------------------------------

    is_active = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = (
            "user",
            "course"
        )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.course.title}"
        )


# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfile(models.Model):

    QUALIFICATION_CHOICES = [
        ("10th", "10th"),
        ("12th", "12th"),
        ("Diploma", "Diploma"),
        ("UG", "Undergraduate"),
        ("PG", "Postgraduate"),
        ("PhD", "PhD"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    phone = models.CharField(
        max_length=15,
        unique=True
    )

    qualification = models.CharField(
        max_length=50,
        choices=QUALIFICATION_CHOICES
    )

    college_company = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username


# ============================================================
# LESSON
# ============================================================

class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    lesson_number = models.PositiveIntegerField(
        default=1
    )

    video_url = models.URLField(
        blank=True,
        null=True
    )

    pdf_file = models.FileField(
        upload_to="lessons/pdfs/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "lesson_number"
        ]

    def __str__(self):
        return (
            f"{self.course.title} - "
            f"Lesson {self.lesson_number}: "
            f"{self.title}"
        )


# ============================================================
# LESSON PROGRESS
# ============================================================

class LessonProgress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_progress"
    )

    completed = models.BooleanField(
        default=False
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = (
            "user",
            "lesson"
        )

        ordering = [
            "lesson__lesson_number"
        ]

    def __str__(self):

        status = (
            "Completed"
            if self.completed
            else "Not Completed"
        )

        return (
            f"{self.user.username} - "
            f"{self.lesson.title} - "
            f"{status}"
        )


# ============================================================
# CERTIFICATE
# ============================================================

class Certificate(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    certificate_id = models.CharField(
        max_length=50,
        unique=True
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "user",
            "course"
        )

        ordering = [
            "-issued_at"
        ]

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.course.title} - "
            f"{self.certificate_id}"
        )


# ============================================================
# BATCH
# ============================================================

class Batch(models.Model):

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(
        max_length=200
    )

    batch_code = models.CharField(
        max_length=50,
        unique=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="batches"
    )

    start_date = models.DateField()

    end_date = models.DateField()

    schedule = models.CharField(
        max_length=200,
        blank=True
    )

    instructor = models.CharField(
        max_length=150,
        default="Kameera Technologies"
    )

    maximum_students = models.PositiveIntegerField(
        default=30
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="upcoming"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return (
            f"{self.name} - "
            f"{self.batch_code}"
        )


# ============================================================
# FEE MANAGEMENT
# ============================================================

class StudentFee(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Partial", "Partial Paid"),
        ("Paid", "Full Paid"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_fees"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="student_fees"
    )

    # --------------------------------------------------------
    # FEE DETAILS
    # --------------------------------------------------------

    course_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    pending_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )

    last_payment_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

        indexes = [
            models.Index(
                fields=["student"]
            ),
            models.Index(
                fields=["course"]
            ),
            models.Index(
                fields=["payment_status"]
            ),
        ]

    def __str__(self):

        return (
            f"{self.student.username} - "
            f"{self.course.title}"
        )

    @property
    def net_fee(self):
        """
        Actual fee after discount.
        """

        return max(
            self.course_fee - self.discount,
            ZERO_DECIMAL
        )

    @property
    def balance(self):
        """
        Remaining amount to be paid.
        """

        return max(
            self.net_fee - self.paid_amount,
            ZERO_DECIMAL
        )

    def recalculate_payment_totals(self):
        """
        Recalculate paid amount from payment transactions.
        """

        self.paid_amount = (
            self.payments.aggregate(
                total=Sum("amount")
            )["total"]
            or ZERO_DECIMAL
        )

        self.update_payment_status()

    def update_payment_status(self):
        """
        Automatically calculate pending amount
        and payment status.
        """

        self.pending_amount = self.balance

        if self.paid_amount <= 0:

            self.payment_status = "Pending"

        elif self.paid_amount >= self.net_fee:

            self.payment_status = "Paid"

            self.paid_amount = self.net_fee
            self.pending_amount = ZERO_DECIMAL

        else:

            self.payment_status = "Partial"

    def save(self, *args, **kwargs):

        self.update_payment_status()

        super().save(
            *args,
            **kwargs
        )


# ============================================================
# PAYMENT TRANSACTIONS
# ============================================================

class Payment(models.Model):

    PAYMENT_MODE_CHOICES = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Bank Transfer", "Bank Transfer"),
        ("Card", "Card"),
    ]

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateField()

    payment_mode = models.CharField(
        max_length=30,
        choices=PAYMENT_MODE_CHOICES
    )

    transaction_reference = models.CharField(
        max_length=150,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-payment_date",
            "-created_at"
        ]

        indexes = [
            models.Index(
                fields=["payment_date"]
            ),
            models.Index(
                fields=["payment_mode"]
            ),
        ]

    def __str__(self):

        return (
            f"{self.student_fee.student.username} - "
            f"₹{self.amount}"
        )