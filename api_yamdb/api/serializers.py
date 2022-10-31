from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from reviews.models import Categories, Comments, Genres, Review, Title, User


class ReviewsSerializers(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    score = serializers.IntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)]
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise serializers.ValidationError('Отзыв уже существует!')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentsSerializers(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text'
    )

    class Meta:
        model = Comments
        fields = '__all__'


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitlesPostSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects.all()
    )
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genres.objects.all(),
        many=True
    )
    year = serializers.IntegerField(
        validators=(
            MinValueValidator(0,
                              message='Год не может быть отрицательным.'),
            MaxValueValidator(timezone.now().year,
                              message='Год не может быть больше настоящего.'),
        )
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitlesGetSerializer(serializers.ModelSerializer):
    genre = GenresSerializer(
        read_only=True,
        many=True
    )
    category = CategoriesSerializer(
        read_only=True
    )
    rating = serializers.SerializerMethodField()

    def get_rating(self, title):
        reviews = Review.objects.filter(title=title)
        if reviews.count() == 0:
            return None

        rating = reviews.aggregate(Avg('score'))['score__avg']
        return round(rating)

    class Meta:
        model = Title
        fields = '__all__'


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'email',
            'username'
        )
        model = User

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено'
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'confirmation_code',
            'username'
        )


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User


class UserOrReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role'
        )
        model = User
        read_only_fields = ('role',)
