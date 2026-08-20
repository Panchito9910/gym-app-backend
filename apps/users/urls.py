from rest_framework.routers import DefaultRouter

from .favorites_views import UserExerciseViewSet
from .views import RoleViewSet, UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'my-exercises', UserExerciseViewSet, basename='my-exercise')

urlpatterns = router.urls
