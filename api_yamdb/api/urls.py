from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import CommentsViewSet, ReviewsViewSet, UserViewSet, \
    CategoriesViewSet, GenresViewSet, TitlesViewSet, registration, token


router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments',
)
router.register('users', UserViewSet)
router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)
router.register('titles', TitlesViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', registration),
    path('v1/auth/token/', token),
]
