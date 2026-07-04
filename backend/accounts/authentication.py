import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from .models import UserRole


User = get_user_model()


def initialize_firebase():
    if firebase_admin._apps:
        return

    cred = credentials.ApplicationDefault()

    firebase_admin.initialize_app(cred)


initialize_firebase()


class FirebaseAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        authorization_header = authentication.get_authorization_header(
            request
        ).split()

        if not authorization_header:
            return None

        if authorization_header[0].lower() != self.keyword.lower().encode():
            return None

        if len(authorization_header) == 1:
            raise exceptions.AuthenticationFailed(
                "Firebase ID token is missing."
            )

        if len(authorization_header) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid Authorization header."
            )

        try:
            id_token = authorization_header[1].decode("utf-8")

        except UnicodeError:
            raise exceptions.AuthenticationFailed(
                "Invalid Firebase ID token."
            )

        try:
            decoded_token = auth.verify_id_token(
                id_token
            )

        except auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed(
                "Firebase ID token has expired."
            )

        except auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed(
                "Firebase ID token has been revoked."
            )

        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed(
                "Invalid Firebase ID token."
            )

        except Exception:
            raise exceptions.AuthenticationFailed(
                "Firebase authentication failed."
            )

        firebase_uid = decoded_token.get("uid")

        if not firebase_uid:
            raise exceptions.AuthenticationFailed(
                "Firebase UID is missing."
            )

        user = self.get_or_create_user(
            firebase_uid=firebase_uid,
            decoded_token=decoded_token,
        )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                "User account is disabled."
            )

        return (
            user,
            decoded_token,
        )

    def get_or_create_user(
        self,
        *,
        firebase_uid,
        decoded_token,
    ):
        email = decoded_token.get(
            "email",
            "",
        )

        phone_number = decoded_token.get(
            "phone_number",
            "",
        )

        user = User.objects.filter(
            firebase_uid=firebase_uid,
        ).first()

        if user:
            self.update_user_identity(
                user=user,
                email=email,
                phone_number=phone_number,
            )

            return user

        username = self.generate_username(
            firebase_uid=firebase_uid,
        )

        user = User.objects.create(
            username=username,
            email=email,
            phone_number=phone_number,
            firebase_uid=firebase_uid,
            role=UserRole.CLIENT,
            is_verified=True,
        )

        user.set_unusable_password()

        user.save(
            update_fields=[
                "password",
            ]
        )

        return user

    def update_user_identity(
        self,
        *,
        user,
        email,
        phone_number,
    ):
        update_fields = []

        if email and user.email != email:
            user.email = email

            update_fields.append(
                "email"
            )

        if (
            phone_number
            and user.phone_number != phone_number
        ):
            user.phone_number = phone_number

            update_fields.append(
                "phone_number"
            )

        if not user.is_verified:
            user.is_verified = True

            update_fields.append(
                "is_verified"
            )

        if update_fields:
            user.save(
                update_fields=update_fields
            )

    def generate_username(
        self,
        *,
        firebase_uid,
    ):
        base_username = (
            f"citizen_{firebase_uid[:20]}"
        )

        username = base_username
        counter = 1

        while User.objects.filter(
            username=username
        ).exists():
            username = (
                f"{base_username}_{counter}"
            )

            counter += 1

        return username

    def authenticate_header(self, request):
        return self.keyword