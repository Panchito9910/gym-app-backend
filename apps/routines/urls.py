from rest_framework.routers import DefaultRouter

from .views import RoutineViewSet

app_name = 'routines'

router = DefaultRouter()
router.register(r'my-routines', RoutineViewSet, basename='my-routine')

urlpatterns = router.urls
