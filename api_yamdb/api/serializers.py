import re

from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.models import Comment, Title, Review, Category, Genre
from users.models import User

MIN_VALUE = 0
MAX_VALUE = 10


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
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
        fields = '__all__'
        model = Review
        extra_kwargs = {
            'title': {'write_only': True},
        }


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзывам."""

    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
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
        title_get_serializer = TitleGetSerializer(instance)
        return title_get_serializer.data


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использование имени "me" в качестве username запрещено.'
            )
        regex = re.compile(r'^[\w.@+-]+\Z')
        if not regex.match(value):
            raise serializers.ValidationError(
                'Неверное значение username. '
                'Допустимы только буквы, цифры, символы ".", "@", "+" и "-".'
            )
        return value


class UsersSerilizer(SignUpSerializer):
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
        read_only_fields = ('role',)


class UsersSerilizerForAdmin(SignUpSerializer):
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


class TokenSerializer(serializers.Serializer):
    """Сериализатор токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
