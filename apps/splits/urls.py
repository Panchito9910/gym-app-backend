from rest_framework.routers import DefaultRouter

from .views import SplitViewSet, UserSplitViewSet

app_name = 'splits'

router = DefaultRouter()
router.register(r'splits', SplitViewSet, basename='split')
router.register(r'my-splits', UserSplitViewSet, basename='my-split')

urlpatterns = router.urls
