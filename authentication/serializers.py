from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    is_librarian = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_librarian"]

    def get_is_librarian(self, user):
        return user.is_superuser or user.groups.filter(name="Librarian").exists()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    token = serializers.CharField(source="auth_token.key", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "token"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Já existe um usuário com este e-mail.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "As senhas não conferem."})

        # Usa os validadores de senha configurados em AUTH_PASSWORD_VALIDATORS.
        user = User(username=attrs["username"], email=attrs["email"])
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        # create_user gera o hash da senha. O usuário novo não entra em nenhum
        # grupo, então é sempre membro (nunca bibliotecário).
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
