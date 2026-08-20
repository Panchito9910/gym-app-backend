from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, IntensityTechniqueViewSet, MuscleViewSet

app_name = 'catalog'

router = DefaultRouter()
router.register(r'muscles', MuscleViewSet, basename='muscle')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'intensity-techniques', IntensityTechniqueViewSet, basename='intensity-technique')

urlpatterns = router.urls
