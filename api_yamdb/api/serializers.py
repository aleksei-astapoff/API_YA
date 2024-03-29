from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework import serializers

from api_yamdb.settings import EMAIL_HOST_USER
from reviews.models import Comment, Title, Review, Category, Genre
from users.models import User, MAX_EMAIL_LENGTH, MAX_FIELD_LENGTH
from users.validators import validate_username


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(title=title_id, author=author).exists():
            raise ValidationError('Нельзя дублировать отзыв!')
        return data

    class Meta:
        fields = ('id', 'text', 'pub_date', 'score', 'author')
        model = Review
        extra_kwargs = {
            'title': {'write_only': True},
        }


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'pub_date', 'author')
        model = Comment
        extra_kwargs = {
            'review': {'write_only': True},
        }


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий произведений."""

    class Meta:
        model = Category
        fields = (
            'name',
            'slug'
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров произведений."""

    class Meta:
        model = Genre
        fields = (
            'name',
            'slug'
        )


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для безопасных запросов."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    rating = serializers.IntegerField(
        read_only=True,
        default=None,
    )

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = (
            'id',
            'name',
            'year',
            'description'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        return TitleGetSerializer(instance).data


class SignUpSerializer(serializers.Serializer):
    """Сериализатор регистрации пользователя."""
    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LENGTH
    )
    username = serializers.CharField(
        required=True,
        max_length=MAX_FIELD_LENGTH,
        validators=(validate_username,)
    )

    def create(self, validated_data):
        try:
            user, created = User.objects.get_or_create(
                username=validated_data.get('username'),
                email=validated_data.get('email'),
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    'detail': ['Имя пользователя или почта уже заняты.']
                }
            )
        send_mail(
            'Подтверждение регистрации',
            'Код подтверждения: '
            f'{default_token_generator.make_token(user)}',
            EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return user


class UsersSerilizerForAdmin(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UsersSerilizer(UsersSerilizerForAdmin):
    """Сериализатор пользователей."""

    class Meta(UsersSerilizerForAdmin.Meta):
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer):
    """Сериализатор токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
