"""
URL configuration for seven_spaces project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import SimpleRouter

from platform_7s.views import LoginAPIView, ApplicationsViewSet, \
    CollectionViewSet, CollectionAddItemAPIView, \
    CollectionCreateAPIView, ObjectViewSet, UnitViewSet, CollectionRemoveItemAPIView, CollectionSetQuantityAPIView, \
    CollectionDeleteAPIView, CollectionCopyAPIView, BookingCreateAPIView, UserBookingListAPIView, \
    ShareCollectionView, GetSharedCollectionView, register_user, create_payment_session, SubscribtionViewSet

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = SimpleRouter()
router.register(r'api/register', ApplicationsViewSet)
#router.register(r'api/objects/dubai', ObjectDubaiViewSet)
#router.register(r'api/objects/abu_dhabi', ObjectAbuDhabiViewSet)
#router.register(r'api/units/dubai', UnitDubaiViewSet)
#router.register(r'api/units/abu_dhabi', UnitAbuDhabiViewSet)
router.register(r'api/collection/get', CollectionViewSet, basename='get-collections')

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/register-user/', register_user, name='register_user'),
    path('api/collection/add_item/', CollectionAddItemAPIView.as_view(), name='collection-add-item'),
    path('api/collection/del_item/', CollectionRemoveItemAPIView.as_view(), name='collection-add-item'),
    path('api/collection/create/', CollectionCreateAPIView.as_view(), name='collection-create'),
    path('api/collection/set-unit-quantity/', CollectionSetQuantityAPIView.as_view(), name='collection-set-unit-quantity'),
    path('api/collection/delete/', CollectionDeleteAPIView.as_view(), name='collection-delete'),
    path('api/collection/copy/', CollectionCopyAPIView.as_view(), name='collection-copy'),
    path('api/objects/', ObjectViewSet.as_view({'get': 'list'}), name='object-list'),
    path('api/units/', UnitViewSet.as_view({'get': 'list'}), name='unit-list'),
    path('api/booking/create', BookingCreateAPIView.as_view(), name='booking-create'),
    path('api/booking/get', UserBookingListAPIView.as_view(), name='booking-get'),
    path('api/collection/share/<int:collection_id>/', ShareCollectionView.as_view(), name='share_collection'),
    path('api/collection/get-shared/<int:collection_id>/', GetSharedCollectionView.as_view(), name='get-shared-collection'),
    path('api/create-payment-session/', create_payment_session, name='create-payment-session'),
    path('api/subscribtions/', SubscribtionViewSet.as_view(), name='get-subscribtions'),
    path('', include(router.urls)),
]
