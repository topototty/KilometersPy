import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect

from KilometersApp.models import Profile

def userLogin(request):
    form = AuthenticationForm(request, data=request.POST or None)
    errors = {}

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Проверяем, это email или логин
        if '@' in username_or_email:
            try:
                # Получаем username по email
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = None
        else:
            username = username_or_email

        # Пытаемся аутентифицировать пользователя
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            errors['login'] = 'Неправильный логин/email или пароль.'

    return render(request, 'Auth/authorization.html', {'form': form, 'errors': errors})


def registration(request):
    errors = {}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Валидация имени пользователя
        if not username:
            errors['username'] = 'Имя пользователя обязательно.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Пользователь с таким именем уже существует.'

        # Валидация email
        if not email:
            errors['email'] = 'Email обязателен.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Этот email уже используется.'

        # Валидация номера телефона
        phone_pattern = r'^\+7-\d{3}-\d{3}-\d{2}-\d{2}$'
        if not phone:
            errors['phone'] = 'Номер телефона обязателен.'
        elif not re.match(phone_pattern, phone):
            errors['phone'] = 'Введите номер телефона в формате +7-XXX-XXX-XX-XX.'

        # Валидация паролей
        if not password1 or not password2:
            errors['password1'] = 'Пароль обязателен.'
        elif password1 != password2:
            errors['password2'] = 'Пароли не совпадают.'
        elif len(password1) < 6:
            errors['password1'] = 'Пароль должен быть не менее 6 символов.'

        if not errors:
            # Создаём пользователя
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Добавляем пользователя в группу
            group, _ = Group.objects.get_or_create(name='User')
            user.groups.add(group)

            # Создаём профиль и шифруем номер телефона
            profile = Profile.objects.create(user=user)
            profile.phone = phone  # Номер шифруется автоматически
            profile.save()

            # Выполняем автоматический вход после регистрации
            login(request, user)
            return redirect('home')

    return render(request, 'Auth/registration.html', {'errors': errors})


def user_logout(request):
    logout(request)
    return redirect("login")
