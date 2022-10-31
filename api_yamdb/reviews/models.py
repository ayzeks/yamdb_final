from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
        (USER, USER),
    ]

    username = models.CharField(
        'Пользователь',
        max_length=150,
        unique=True,
        null=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=50,
        choices=ROLES,
        default=USER,
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ['id']


class Categories(models.Model):
    name = models.TextField(
        max_length=250,
        blank=False,
        verbose_name='Наименование категории'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Адрес'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Genres(models.Model):
    name = models.TextField(
        max_length=250,
        verbose_name='Наименование жанра'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Адрес'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Title(models.Model):
    name = models.TextField(
        max_length=250,
        blank=False,
        verbose_name='Наименование произведения',
        db_index=True
    )
    category = models.ForeignKey(
        Categories,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категории',
        db_index=True
    )
    genre = models.ManyToManyField(
        Genres,
        blank=True,
        verbose_name='Жанры',
        db_index=True
    )
    description = models.TextField()
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Год выхода',
        db_index=True,
        validators=(MaxValueValidator(
            timezone.now().year,
            message='Год не может быть больше текущего.'),)
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название',
        db_index=True
    )
    text = models.TextField(verbose_name='Текст отзыва')
    pub_date = models.DateTimeField(
        verbose_name='Дата отзыва',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Оценка',
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    text = models.TextField(verbose_name='Текст комментария',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        db_index=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
