import os
import requests
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from . import forms, models


# Create your views here.
class LoginView(FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    initial = {
        "first_name": "black",
        "last_name": "pink",
        "email": "blackpink@gmail.com",
    }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        # user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do: add succes message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GITHUB_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GITHUB_ID")
        client_secret = os.environ.get("GITHUB_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException()
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    # there is no name and no bio in GITHUB
                    if name is None:
                        name = username
                    if bio is None:
                        bio = ""
                    # there is no name and no bio in GITHUB
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException()
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException()
        else:
            raise GithubException()
    except GithubException:
        return redirect(reverse("users:login"))


def kakao_login(request):
    REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
    REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
        REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException()
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        print(profile_json)
        email = profile_json.get("kakao_account").get("email")
        nickname = profile_json.get("kakao_account").get("profile").get("nickname")
        profile_image = (
            profile_json.get("kakao_account").get("profile").get("profile_image_url")
        )
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException()
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )
        login(request, user)
        return redirect(reverse("core:home"))
    except KakaoException:
        return redirect(reverse("users:login"))


{
    "id": 1657908716,
    "connected_at": "2021-03-11T15:09:23Z",
    "properties": {
        "nickname": "Henry",
        "profile_image": "http://k.kakaocdn.net/dn/0X0yC/btqAXukhi36/dlmN0Q0BVZVntPrOlF1JaK/img_640x640.jpg",
        "thumbnail_image": "http://k.kakaocdn.net/dn/0X0yC/btqAXukhi36/dlmN0Q0BVZVntPrOlF1JaK/img_110x110.jpg",
    },
    "kakao_account": {
        "profile_needs_agreement": False,
        "profile": {
            "nickname": "Henry",
            "thumbnail_image_url": "http://k.kakaocdn.net/dn/0X0yC/btqAXukhi36/dlmN0Q0BVZVntPrOlF1JaK/img_110x110.jpg",
            "profile_image_url": "http://k.kakaocdn.net/dn/0X0yC/btqAXukhi36/dlmN0Q0BVZVntPrOlF1JaK/img_640x640.jpg",
        },
        "has_email": True,
        "email_needs_agreement": False,
        "is_email_valid": True,
        "is_email_verified": True,
        "email": "fan2soft@gmail.com",
    },
}
