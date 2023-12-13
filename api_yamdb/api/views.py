# from random import randint
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import (IsAdminOnly, IsAdminOrUserOrReadOnly,
                          IsAdminOrModeratorOrAuthorOnly)
from .serializers import (CommentSerializer, ReviewSerializer,
                          SignUpSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer,
                          TokenSerializer)
from reviews.models import Review, Title, Category, Genre
from users.models import EmailVerification, User


class UsersViewSet(viewsets.ModelViewSet):
    '''Вьюсет для Пользователя'''

    permission_classes = (IsAuthenticated, IsAdminOnly,)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для Категорий'''

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'slug')
    permission_classes = (IsAdminOrUserOrReadOnly,)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для Жанров'''

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'slug')
    permission_classes = (IsAdminOrUserOrReadOnly,)


class TitleViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для Произведений'''
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category')
    permission_classes = (IsAdminOrUserOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    '''Вьюсет для Комментариев'''

    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrModeratorOrAuthorOnly,)

    def get_review(self):
        return get_object_or_404(
            Review, id=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    '''Вьюсет для Отзывов'''

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrModeratorOrAuthorOnly,)

    def get_title(self):
        return get_object_or_404(
            Title, id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class SignUpView(APIView):
    """Эндпоинт для регистрации пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса."""
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            email_verification = EmailVerification.objects.create(
                confirmation_code=(EmailVerification.
                                   generate_confirmation_code(self)),
                user=user,
            )
            email_verification.send_verification_email()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class TokenView(TokenObtainPairView):

#     serializer_class = MyTokenObtainPairSerializer


class ObtainTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data["username"]
        )

        if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
        ):
            token = AccessToken.for_user(user)
            return Response({"token": str(token)}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
