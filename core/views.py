from rest_framework import viewsets, status, permissions,serializers
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import User, Vendor, Product, Order, OrderItem
from .serializers import UserSerializer, VendorSerializer, ProductSerializer, OrderSerializer
from .permissions import IsAdmin, IsVendor, IsCustomer, IsVendorOwner

@api_view(['POST'])
def CreateUser(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role', 'customer')  

        if not all([username, email, password]):
            return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        user.save()
        return Response({'message': 'User created successfully', 'user': username}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        try:
            user = serializer.save()
            user.set_password(user.password)
            user.save()
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.select_related('user').all()
    serializer_class = VendorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdmin | IsVendor]
        else:
            permission_classes = [IsAdmin | (IsVendor & IsVendorOwner)]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('vendor__user').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vendor', 'name', 'price']
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsVendor & IsVendorOwner]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        try:
            serializer.save(vendor=self.request.user.vendor)
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related('items__product__vendor').all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsCustomer]
        elif self.action == 'list':
            permission_classes = [IsAdmin | IsVendor | IsCustomer]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'vendor':
            return Order.objects.filter(items__product__vendor=user.vendor).distinct()
        elif user.role == 'customer':
            return Order.objects.filter(customer=user)
        return super().get_queryset()

    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def place_order(self, request):
        try:
            items_data = request.data.get('items', [])
            if not items_data:
                return Response({'error': 'No items provided.'}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(customer=request.user)
            total = 0

            for item_data in items_data:
                product = get_object_or_404(Product, id=item_data['product_id'])

                if product.stock < item_data['quantity']:
                    return Response({'error': f'Insufficient stock for {product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=product.price
                )

                product.stock -= item_data['quantity']
                product.save()

                total += product.price * item_data['quantity']

            order.total = total
            order.save()

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
