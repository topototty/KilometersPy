import re

from django import forms
from django.contrib.auth.models import User, Group
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from KilometersApp.models import DriversLicenseCategoryType


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'required': True
        })
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
            'required': True
        })
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Группа',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Выберите группу',
            'required': True
        })
    )
    phone = forms.CharField(
        label='Номер телефона',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона в формате +7-XXX-XXX-XX-XX'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Имя пользователя уже занято. Пожалуйста, выберите другое.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'}),
        label="Пароль",
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'}),
        label="Подтверждение пароля",
        required=True
    )

    email = forms.EmailField(
        label="Электронная почта",
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'example@example.com'})
    )
    phone = forms.CharField(
        max_length=16,
        label="Номер телефона",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+7-000-000-00-00'})
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Группа",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z]{5,15}$', username):
            raise forms.ValidationError(
                "Имя пользователя должно содержать только латинские буквы и быть длиной от 5 до 15 символов (без пробелов)."
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password1):
            raise forms.ValidationError(
                "Пароль должен содержать минимум одну латинскую букву, одну цифру, один специальный символ и быть длиной от 8 символов."
            )
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_regex = r'^\+7-\d{3}-\d{3}-\d{2}-\d{2}$'
        if not re.match(phone_regex, phone):
            raise forms.ValidationError("Номер телефона должен быть в формате +7-000-000-00-00.")
        if User.objects.filter(profile__encrypted_phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            group = self.cleaned_data.get('group')
            if group:
                user.groups.add(group)
        return user


from django.contrib.auth.models import Group
from django import forms
from .models import User, Driver


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Оставьте пустым, если не хотите менять'}),
        label="Пароль",
        required=False
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Оставьте пустым, если не хотите менять'}),
        label="Подтверждение пароля",
        required=False
    )
    phone = forms.CharField(
        max_length=16,
        label="Номер телефона",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+7-000-000-00-00'})
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Группа",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Пароли не совпадают.")
            if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password1):
                raise forms.ValidationError(
                    "Пароль должен содержать минимум одну латинскую букву, одну цифру, один специальный символ и быть длиной от 8 символов."
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")

        # Получаем предыдущую группу
        previous_group = self.instance.groups.first()  # Предположим, что пользователь только в одной группе

        if previous_group and previous_group.name == "Driver" and 'group' in self.cleaned_data:
            new_group = self.cleaned_data['group']
            if new_group.name != "Driver":
                try:
                    driver = Driver.objects.get(user_id=self.instance)
                    driver.delete()
                except Driver.DoesNotExist:
                    pass

        if password1:
            user.set_password(password1)

        if commit:
            user.save()
            group = self.cleaned_data.get('group')
            if group:
                user.groups.clear()
                user.groups.add(group)

        return user


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['user_id', 'drivers_license_number', 'date_of_issue_of_drivers_license',
                  'expiration_date_of_drivers_license', 'license_categories']

        license_categories = forms.ModelMultipleChoiceField(
            queryset=DriversLicenseCategoryType.objects.all(),
            widget=forms.CheckboxSelectMultiple
        )

    def clean_date_of_issue_of_drivers_license(self):
        date_of_issue = self.cleaned_data.get('date_of_issue_of_drivers_license')
        if date_of_issue > timezone.now().date():
            raise ValidationError('Дата выдачи водительского удостоверения не может быть в будущем.')
        return date_of_issue

    def clean_expiration_date_of_drivers_license(self):
        expiration_date = self.cleaned_data.get('expiration_date_of_drivers_license')
        if expiration_date < timezone.now().date():
            raise ValidationError('Срок действия водительского удостоверения истек.')
        return expiration_date

    def clean_user_id(self):
        user = self.cleaned_data.get('user_id')
        if not user.groups.filter(name='Driver').exists():
            raise ValidationError('Пользователь должен быть в группе "Driver".')
        return user

    def clean(self):
        cleaned_data = super().clean()
        date_of_issue = cleaned_data.get('date_of_issue_of_drivers_license')
        expiration_date = cleaned_data.get('expiration_date_of_drivers_license')
        if date_of_issue and expiration_date and expiration_date < date_of_issue:
            self.add_error('expiration_date_of_drivers_license',
                           'Дата окончания действия не может быть раньше даты выдачи.')
        return cleaned_data
