from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

MAX_LENGTH = 256
TEXT_LIMIT_SHOW = 20
SLUG_LIMIT = 50


class Category(models.Model):
    """Модель категории."""
    name = models.CharField(verbose_name='Название',
                            max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True,
                            verbose_name='Слаг',
                            max_length=SLUG_LIMIT)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанра произведений."""
    name = models.CharField(verbose_name='Название',
                            max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True,
                            verbose_name='Слаг',
                            max_length=SLUG_LIMIT)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(verbose_name='Название',
                            max_length=MAX_LENGTH)
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(verbose_name='Описание', blank=True)
    genre = models.ManyToManyField(Genre,
                                   verbose_name='Жанр')
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 verbose_name='Категория')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def clean(self):
        if self.year > timezone.now().year:
            raise ValidationError('Год выпуска не может быть больше текущего!')

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель Отзывов."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.CharField(
        max_length=MAX_LENGTH
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        verbose_name='Автор'
    )
    score = models.IntegerField(
        'Оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Диапазон от 1 до 10!'}
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'reviews'
        ordering = ('author', '-pub_date')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )]

    def __str__(self):
        return (
            f'Title: {self.title[:TEXT_LIMIT_SHOW]}, '
            f'Text: {self.text[:TEXT_LIMIT_SHOW]}, '
            f'Author: {self.author}, '
            f'Date: {self.pub_date}, '
            f'Score: {self.score}'
        )


class Comment(models.Model):
    """Модель Комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.CharField(
        'Текст комментария',
        max_length=MAX_LENGTH
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('author', '-pub_date')
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f'Review: {self.review[:TEXT_LIMIT_SHOW]}, '
            f'Text: {self.text[:TEXT_LIMIT_SHOW]}, '
            f'Author: {self.author}, '
            f'Date: {self.pub_date}, '
        )