from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import (
    StudentProfile,
    Course,
    Lesson,
    Batch,
    StudentFee,
    Payment,
)


# ============================================================
# STUDENT REGISTRATION FORM
# ============================================================

class StudentRegistrationForm(forms.Form):

    first_name = forms.CharField(
        max_length=100,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your first name",
            }
        )
    )

    last_name = forms.CharField(
        max_length=100,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your last name",
            }
        )
    )

    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Choose a username",
            }
        )
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
            }
        )
    )

    phone = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your phone number",
            }
        )
    )

    qualification = forms.ChoiceField(
        choices=StudentProfile.QUALIFICATION_CHOICES,
        label="Qualification",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        )
    )

    college_company = forms.CharField(
        max_length=200,
        required=False,
        label="College / Company",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter college or company",
            }
        )
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
            }
        )
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password",
            }
        )
    )

    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean_phone(self):

        phone = self.cleaned_data["phone"]

        if StudentProfile.objects.filter(
            phone=phone
        ).exists():

            raise forms.ValidationError(
                "This phone number is already registered."
            )

        return phone

    def clean_password(self):

        password = self.cleaned_data["password"]

        validate_password(password)

        return password

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get(
            "password"
        )

        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if password and confirm_password:

            if password != confirm_password:

                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


# ============================================================
# STUDENT PROFILE EDIT FORM
# ============================================================

class StudentProfileEditForm(forms.Form):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your first name",
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your last name",
            }
        )
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
            }
        )
    )

    phone = forms.CharField(
        max_length=15,
        required=True,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your phone number",
            }
        )
    )

    qualification = forms.ChoiceField(
        choices=StudentProfile.QUALIFICATION_CHOICES,
        required=True,
        label="Qualification",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        )
    )

    college_company = forms.CharField(
        max_length=200,
        required=False,
        label="College / Company",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter college or company",
            }
        )
    )

    def __init__(
        self,
        *args,
        user=None,
        profile=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.user = user
        self.profile = profile

        if not self.is_bound:

            if user:

                self.fields["first_name"].initial = (
                    user.first_name
                )

                self.fields["last_name"].initial = (
                    user.last_name
                )

                self.fields["email"].initial = (
                    user.email
                )

            if profile:

                self.fields["phone"].initial = (
                    profile.phone
                )

                self.fields["qualification"].initial = (
                    profile.qualification
                )

                self.fields["college_company"].initial = (
                    profile.college_company
                )

    def clean_email(self):

        email = self.cleaned_data["email"].strip()

        queryset = User.objects.filter(
            email__iexact=email
        )

        if self.user:

            queryset = queryset.exclude(
                pk=self.user.pk
            )

        if queryset.exists():

            raise forms.ValidationError(
                "This email address is already being used."
            )

        return email

    def clean_phone(self):

        phone = self.cleaned_data["phone"].strip()

        queryset = StudentProfile.objects.filter(
            phone=phone
        )

        if self.profile:

            queryset = queryset.exclude(
                pk=self.profile.pk
            )

        if queryset.exists():

            raise forms.ValidationError(
                "This phone number is already registered."
            )

        return phone


# ============================================================
# ADMIN COURSE FORM
# ============================================================

class CourseAdminForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            "title",
            "slug",
            "short_description",
            "description",
            "category",
            "duration",
            "level",
            "price",
            "instructor",
            "image",
            "is_active",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Course title",
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "course-slug",
                }
            ),

            "short_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Short course description",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Full course description",
                }
            ),

            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Data Analytics",
                }
            ),

            "duration": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "8 Weeks",
                }
            ),

            "level": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Beginner",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "instructor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kameera Technologies",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


# ============================================================
# ADMIN LESSON FORM
# ============================================================

class LessonAdminForm(forms.ModelForm):

    class Meta:

        model = Lesson

        fields = [
            "title",
            "lesson_number",
            "description",
            "video_url",
            "pdf_file",
            "is_active",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Lesson title",
                }
            ),

            "lesson_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1",
                    "min": "1",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": (
                        "Explain what students will learn "
                        "in this lesson."
                    ),
                }
            ),

            "video_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "https://www.youtube.com/watch?v=..."
                    ),
                }
            ),

            "pdf_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


# ============================================================
# BACKWARD-COMPATIBILITY ALIAS
# ============================================================

LessonForm = LessonAdminForm


# ============================================================
# ADMIN BATCH FORM
# ============================================================

class BatchAdminForm(forms.ModelForm):

    class Meta:

        model = Batch

        fields = [
            "name",
            "batch_code",
            "course",
            "start_date",
            "end_date",
            "schedule",
            "instructor",
            "maximum_students",
            "status",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Power BI August 2026",
                }
            ),

            "batch_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "PBI-AUG-2026-01",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "schedule": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Monday - Friday, "
                        "7:00 PM - 8:30 PM"
                    ),
                }
            ),

            "instructor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kameera Technologies",
                }
            ),

            "maximum_students": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "30",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        start_date = cleaned_data.get(
            "start_date"
        )

        end_date = cleaned_data.get(
            "end_date"
        )

        maximum_students = cleaned_data.get(
            "maximum_students"
        )

        if (
            start_date
            and end_date
            and end_date < start_date
        ):

            self.add_error(
                "end_date",
                "End date cannot be earlier than start date."
            )

        if (
            maximum_students is not None
            and maximum_students < 1
        ):

            self.add_error(
                "maximum_students",
                "Maximum students must be at least 1."
            )

        return cleaned_data


# ============================================================
# ADMIN - STUDENT FEE FORM
# ============================================================

class StudentFeeAdminForm(forms.ModelForm):

    class Meta:

        model = StudentFee

        fields = [
            "student",
            "course",
            "course_fee",
            "discount",
            "notes",
        ]

        widgets = {

            "student": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "course_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter course fee",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter discount",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Optional payment notes",
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields["student"].queryset = (
            User.objects
            .filter(
                is_staff=False,
                is_superuser=False
            )
            .order_by(
                "first_name",
                "last_name",
                "username"
            )
        )

        self.fields["student"].label_from_instance = (
            lambda user:
            f"{user.get_full_name() or user.username} "
            f"({user.username})"
        )

        self.fields["course"].queryset = (
            Course.objects
            .filter(
                is_active=True
            )
            .order_by(
                "title"
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        course_fee = cleaned_data.get(
            "course_fee"
        )

        discount = cleaned_data.get(
            "discount"
        )

        if (
            course_fee is not None
            and course_fee < 0
        ):

            raise forms.ValidationError(
                "Course fee cannot be negative."
            )

        if (
            discount is not None
            and discount < 0
        ):

            raise forms.ValidationError(
                "Discount cannot be negative."
            )

        if (
            course_fee is not None
            and discount is not None
            and discount > course_fee
        ):

            raise forms.ValidationError(
                "Discount cannot be greater than the course fee."
            )

        return cleaned_data


# ============================================================
# ADMIN - PAYMENT FORM
# ============================================================

class PaymentAdminForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = [
            "amount",
            "payment_date",
            "payment_mode",
            "transaction_reference",
            "notes",
        ]

        widgets = {

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter payment amount",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),

            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "payment_mode": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "transaction_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "UPI / Bank / Card reference"
                    ),
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Optional payment notes"
                    ),
                }
            ),
        }

    def __init__(
        self,
        *args,
        student_fee=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.student_fee = student_fee

    def clean_amount(self):

        amount = self.cleaned_data.get(
            "amount"
        )

        if amount is None:
            return amount

        if amount <= 0:

            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        if self.student_fee:

            remaining = self.student_fee.balance

            if amount > remaining:

                raise forms.ValidationError(
                    f"Payment cannot exceed the pending "
                    f"amount of ₹{remaining}."
                )

        return amount