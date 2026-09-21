from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, GuestViewSet, BookingViewSet, index

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('styles.css', serve, {'document_root': settings.STATIC_DIR, 'path': 'styles.css'}),
    path('script.js', serve, {'document_root': settings.STATIC_DIR, 'path': 'script.js'}),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DIR)

