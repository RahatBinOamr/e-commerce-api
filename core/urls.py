from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateUser, UserViewSet, VendorViewSet, ProductViewSet, OrderViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'vendors', VendorViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('create-user/', CreateUser, name='create_user'),  
    path('', include(router.urls)),  
]