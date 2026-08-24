from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import (
    StudentProfile,
    Course,
    Lesson,
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

    # --------------------------------------------------------
    # USERNAME VALIDATION
    # --------------------------------------------------------

    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    # --------------------------------------------------------
    # EMAIL VALIDATION
    # --------------------------------------------------------

    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(
            email=email
        ).exists():

            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    # --------------------------------------------------------
    # PHONE VALIDATION
    # --------------------------------------------------------

    def clean_phone(self):

        phone = self.cleaned_data["phone"]

        if StudentProfile.objects.filter(
            phone=phone
        ).exists():

            raise forms.ValidationError(
                "This phone number is already registered."
            )

        return phone

    # --------------------------------------------------------
    # PASSWORD VALIDATION
    # --------------------------------------------------------

    def clean_password(self):

        password = self.cleaned_data["password"]

        validate_password(password)

        return password

    # --------------------------------------------------------
    # PASSWORD CONFIRMATION
    # --------------------------------------------------------

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
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

            # ------------------------------------------------
            # LESSON TITLE
            # ------------------------------------------------

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter lesson title",
                }
            ),

            # ------------------------------------------------
            # LESSON NUMBER
            # ------------------------------------------------

            "lesson_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1",
                    "min": "1",
                }
            ),

            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

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

            # ------------------------------------------------
            # VIDEO URL
            # ------------------------------------------------

            "video_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "https://www.youtube.com/watch?v=..."
                    ),
                }
            ),

            # ------------------------------------------------
            # PDF FILE
            # ------------------------------------------------

            "pdf_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),

            # ------------------------------------------------
            # ACTIVE
            # ------------------------------------------------

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


# ============================================================
# LESSON FORM ALIAS
# ============================================================
#
# This allows older code using LessonForm to continue working.
#

LessonForm = LessonAdminForm