from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import viewsets, permissions, mixins, status
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAdminOrReadOnly, \
    AdminModerAuthorOrReadOnly, AdminOnly
from .serializers import CommentsSerializers, ReviewsSerializers, \
    CategoriesSerializer, GenresSerializer, SignUpSerializer, \
    TokenSerializer, UserSerializer, TitlesGetSerializer, \
    TitlesPostSerializer, UserOrReadOnlySerializer
from reviews.models import Categories, Genres, User, Title, Review
from .filters import TitlesFilter


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializers
    permission_classes = (AdminModerAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, id=self.kwargs.get('title_id'))
        )


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializers
    permission_classes = (AdminModerAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=title
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=get_object_or_404(Title, id=self.kwargs.get('title_id'))
        )
        serializer.save(
            author=self.request.user,
            review=review
        )


class CreateViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class CategoriesViewSet(CreateViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'


class GenresViewSet(CreateViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filterset_class = TitlesFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitlesGetSerializer
        return TitlesPostSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registration(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    user, created = User.objects.get_or_create(
        email=email,
        username=username
    )
    send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    user = get_object_or_404(
        User,
        username=username
    )

    confirmation_code = serializer.data.get('confirmation_code')

    if not default_token_generator.check_token(
        user,
        confirmation_code
    ):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    token = AccessToken.for_user(user)
    return Response(
        {'token': str(token)}, status=status.HTTP_200_OK
    )


def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Регистрация'
    message = f'Ваш код подтверждения {confirmation_code}'
    user_email = [user.email]
    return send_mail(subject, message, None, user_email)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    lookup_value_regex = r'[\w\@\.\+\-]+'
    permission_classes = (AdminOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        methods=[
            'get',
            'patch',
        ],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserOrReadOnlySerializer,
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
