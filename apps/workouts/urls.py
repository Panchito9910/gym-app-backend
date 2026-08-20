from rest_framework.routers import DefaultRouter

from .views import WorkoutViewSet

app_name = 'workouts'

router = DefaultRouter()
router.register(r'workouts', WorkoutViewSet, basename='workout')

urlpatterns = router.urls
