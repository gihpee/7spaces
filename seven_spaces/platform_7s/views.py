import random
import string

import django_filters
import stripe
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from .bot_utils import send_application, send_collection_link

from platform_7s.models import Applications, Object_Dubai, Object_AbuDhabi, Unit_Dubai, Unit_AbuDhabi, Collection, \
    CollectionUnitsAbuDhabi, CollectionUnitsDubai, Booking, Subscribtion
from platform_7s.serializers import ApplicationsSerializer, ObjectDubaiSerializer, ObjectAbuDhabiSerializer, \
    UnitDubaiSerializer, UnitAbuDhabiSerializer, CollectionSerializer, CollectionCreateSerializer, BookingSerializer, \
    SubscribtionSerializer, PaymentSessionSerializer


class LoginAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful operation",
                examples={
                    "application/json": {
                        "refresh": "string",
                        "access": "string",
                    }
                }
            ),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def post(self, request):
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)
        if username is None or password is None:
            return Response({'error': 'Нужен и логин, и пароль'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'username': user.username
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class ApplicationsViewSet(ModelViewSet):
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        instance = serializer.save()
        send_application(instance.phone_number, instance.agent_fio, instance.email)


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        application = Applications.objects.get(phone_number=phone_number)
        email = application.email
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user = User.objects.create_user(username=phone_number, password=password, email=email)

        send_mail(
            'You are registered on the platform',
            f'Your login: {phone_number}, password: {password}',
            'gmorychev.work@gmail.com',
            [email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'User registered successfully', 'username': phone_number,
                             'password': password, 'email': email})
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


class Pagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class ObjectDubaiFilter(django_filters.FilterSet):
    search_query = django_filters.CharFilter(method='filter_by_search_query', required=False)
    min_price = django_filters.NumberFilter(field_name='overall_min_unit_price', lookup_expr='gte', required=False)
    max_price = django_filters.NumberFilter(field_name='overall_max_unit_price', lookup_expr='lte', required=False)
    min_square = django_filters.NumberFilter(field_name='overall_min_unit_size', lookup_expr='gte', required=False)
    max_square = django_filters.NumberFilter(field_name='overall_max_unit_size', lookup_expr='lte', required=False)
    down_price = django_filters.NumberFilter(field_name='down_price', lookup_expr='gte', required=False)
    num_bedrooms = django_filters.NumberFilter(field_name='units__num_bedrooms', required=False)
    facilities = django_filters.CharFilter(method='filter_by_facilities', required=False)
    min_floor = django_filters.CharFilter(method='filter_by_min_floor', required=False)
    max_floor = django_filters.CharFilter(method='filter_by_max_floor', required=False)
    parking_spaces = django_filters.CharFilter(method='filter_by_parking', required=False)
    sale_type = django_filters.CharFilter(method='filter_by_sale_type', required=False)
    is_floor_plan_view = django_filters.BooleanFilter(field_name='is_floor_plan_view', required=False)
    sale_status = django_filters.CharFilter(method='filter_by_sale_status', required=False)
    id = django_filters.NumberFilter(field_name='id', lookup_expr='exact', required=False)

    class Meta:
        model = Object_Dubai
        fields = ['min_price', 'max_price', 'num_bedrooms']

    def filter_by_search_query(self, queryset, name, value):
        if value:
            return queryset.filter(
                models.Q(name__icontains=value) |
                models.Q(address__icontains=value) |
                models.Q(district__icontains=value)
            )
        return queryset

    def filter_by_facilities(self, queryset, name, value):
        if value:
            facilities_list = value.split(',')
            return queryset.filter(facilities__contains=facilities_list)
        return queryset

    def filter_by_min_floor(self, queryset, name, value):
        if value:
            return queryset.filter(total__unitsMaxFloor__gte=int(value))
        return queryset

    def filter_by_max_floor(self, queryset, name, value):
        if value:
            return queryset.filter(total__unitsMaxFloor__lte=int(value))
        return queryset

    def filter_by_sale_status(self, queryset, name, value):
        if value:
            sale_statuses = value.split(',')
            return queryset.filter(residential_complex_sale_status__in=sale_statuses)
        return queryset

    def filter_by_sale_type(self, queryset, name, value):
        if value:
            sale_types = value.split(',')
            return queryset.filter(sale_type__in=sale_types)
        return queryset

    def filter_by_parking(self, queryset, name, value):
        if value:
            parking = value.split(',')
            return queryset.filter(parking_spaces__in=parking)
        return queryset


class ObjectAbuDhabiFilter(django_filters.FilterSet):
    search_query = django_filters.CharFilter(method='filter_by_search_query', required=False)
    min_price = django_filters.NumberFilter(field_name='overall_min_unit_price', lookup_expr='gte', required=False)
    max_price = django_filters.NumberFilter(field_name='overall_max_unit_price', lookup_expr='lte', required=False)
    min_square = django_filters.NumberFilter(field_name='overall_min_unit_size', lookup_expr='gte', required=False)
    max_square = django_filters.NumberFilter(field_name='overall_max_unit_size', lookup_expr='lte', required=False)
    down_price = django_filters.NumberFilter(field_name='down_price', lookup_expr='gte', required=False)
    num_bedrooms = django_filters.NumberFilter(field_name='units__num_bedrooms', required=False)
    facilities = django_filters.CharFilter(method='filter_by_facilities', required=False)
    min_floor = django_filters.CharFilter(method='filter_by_min_floor', required=False)
    max_floor = django_filters.CharFilter(method='filter_by_max_floor', required=False)
    parking_spaces = django_filters.CharFilter(method='filter_by_parking', required=False)
    sale_type = django_filters.CharFilter(method='filter_by_sale_type', required=False)
    is_floor_plan_view = django_filters.BooleanFilter(field_name='is_floor_plan_view', required=False)
    sale_status = django_filters.CharFilter(method='filter_by_sale_status', required=False)
    id = django_filters.NumberFilter(field_name='id', lookup_expr='exact', required=False)

    class Meta:
        model = Object_AbuDhabi
        fields = ['min_price', 'max_price', 'num_bedrooms']

    def filter_by_search_query(self, queryset, name, value):
        if value:
            return queryset.filter(
                models.Q(name__icontains=value) |
                models.Q(address__icontains=value) |
                models.Q(district__icontains=value)
            )
        return queryset

    def filter_by_facilities(self, queryset, name, value):
        if value:
            facilities_list = value.split(',')
            return queryset.filter(facilities__contains=facilities_list)
        return queryset

    def filter_by_min_floor(self, queryset, name, value):
        if value:
            return queryset.filter(total__unitsMaxFloor__gte=int(value))
        return queryset

    def filter_by_max_floor(self, queryset, name, value):
        if value:
            return queryset.filter(total__unitsMaxFloor__lte=int(value))
        return queryset

    def filter_by_sale_status(self, queryset, name, value):
        if value:
            sale_statuses = value.split(',')
            return queryset.filter(residential_complex_sale_status__in=sale_statuses)
        return queryset

    def filter_by_sale_type(self, queryset, name, value):
        if value:
            sale_types = value.split(',')
            return queryset.filter(sale_type__in=sale_types)
        return queryset

    def filter_by_parking(self, queryset, name, value):
        if value:
            parking = value.split(',')
            return queryset.filter(parking_spaces__in=parking)
        return queryset


"""class ObjectDubaiViewSet(ModelViewSet):
    queryset = Object_Dubai.objects.all()
    serializer_class = ObjectDubaiSerializer
    http_method_names = ['get']
    #permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ObjectDubaiFilter


class ObjectAbuDhabiViewSet(ModelViewSet):
    queryset = Object_AbuDhabi.objects.all()
    serializer_class = ObjectAbuDhabiSerializer
    http_method_names = ['get']
    #permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ObjectAbuDhabiFilter"""


class ObjectViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = None

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'city',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Dubai or AbuDhabi',
        ),
        openapi.Parameter(
            'id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER,
            required=False,
            description='id',
        ),
    ])
    def list(self, request, *args, **kwargs):
        city = request.query_params.get('city')
        if city == 'Dubai':
            self.filterset_class = ObjectDubaiFilter
            queryset = Object_Dubai.objects.all()
            serializer_class = ObjectDubaiSerializer
        elif city == 'AbuDhabi':
            self.filterset_class = ObjectAbuDhabiFilter
            queryset = Object_AbuDhabi.objects.all()
            serializer_class = ObjectAbuDhabiSerializer
        else:
            return Response({'error': 'Invalid city'}, status=status.HTTP_400_BAD_REQUEST)

        self.queryset = queryset  # Set the queryset for pagination
        self.serializer_class = serializer_class  # Set the serializer class for serialization

        return super().list(request, *args, **kwargs)  # Call the base class list method with the request


class UnitViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'city',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Dubai or AbuDhabi',
        ),
        openapi.Parameter(
            'id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER,
            required=False,
            description='id',
        ),
    ])
    def list(self, request, *args, **kwargs):
        city = request.query_params.get('city')
        unit_id = request.query_params.get('id')

        if city == 'Dubai':
            queryset = Unit_Dubai.objects.all()
            serializer_class = UnitDubaiSerializer
        elif city == 'AbuDhabi':
            queryset = Unit_AbuDhabi.objects.all()
            serializer_class = UnitAbuDhabiSerializer
        else:
            return Response({'error': 'Invalid city'}, status=status.HTTP_400_BAD_REQUEST)

        if unit_id:
            queryset = queryset.filter(id=unit_id)

        self.queryset = queryset
        self.serializer_class = serializer_class

        return super().list(request, *args, **kwargs)


"""class UnitDubaiViewSet(ModelViewSet):
    queryset = Unit_Dubai.objects.all()
    serializer_class = UnitDubaiSerializer
    http_method_names = ['get']
    #permission_classes = [IsAuthenticated]


class UnitAbuDhabiViewSet(ModelViewSet):
    queryset = Unit_AbuDhabi.objects.all()
    serializer_class = UnitAbuDhabiSerializer
    http_method_names = ['get']
    #permission_classes = [IsAuthenticated]"""


class CollectionCreateAPIView(generics.CreateAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionCreateSerializer
    permission_classes = [IsAuthenticated]


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return Collection.objects.filter(owner=user)


class SubscribtionViewSet(APIView):
    def get(self, request):
        subscribtions = Subscribtion.objects.all()
        serializer = SubscribtionSerializer(subscribtions, many=True)
        return Response(serializer.data)


class CollectionAddItemAPIView(APIView):
    #permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'collection_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'city': openapi.Schema(type=openapi.TYPE_STRING),
                'item_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'item_type': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            201: "Item added to collection successfully",
        }
    )
    def post(self, request, *args, **kwargs):
        collection_id = request.data.get('collection_id')
        city = request.data.get('city')
        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')

        user = request.user

        collection = get_object_or_404(Collection, id=collection_id, owner=user)

        if item_type == 'Object':
            if city == 'AbuDhabi':
                item_model = Object_AbuDhabi
            elif city == 'Dubai':
                item_model = Object_Dubai
            else:
                return Response({"error": "Invalid city"}, status=status.HTTP_400_BAD_REQUEST)
        elif item_type == 'Unit':
            if city == 'AbuDhabi':
                item_model = Unit_AbuDhabi
            elif city == 'Dubai':
                item_model = Unit_Dubai
            else:
                return Response({"error": "Invalid city"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid item_type"}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(item_model, id=item_id)

        if item_type == 'Unit':
            quantity = 1
        else:
            quantity = None

        if item_model == Object_AbuDhabi:
            collection.objects_abudhabi.add(item)
        elif item_model == Object_Dubai:
            collection.objects_dubai.add(item)
        elif item_model == Unit_AbuDhabi:
            CollectionUnitsAbuDhabi.objects.create(collection=collection, unit=item, quantity=quantity)
        elif item_model == Unit_Dubai:
            CollectionUnitsDubai.objects.create(collection=collection, unit=item, quantity=quantity)

        return Response({"success": "Item added to collection successfully"}, status=status.HTTP_201_CREATED)


class CollectionRemoveItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'collection_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'city': openapi.Schema(type=openapi.TYPE_STRING),
                'item_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'item_type': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: "Item removed from collection successfully",
        }
    )
    def post(self, request, *args, **kwargs):
        collection_id = request.data.get('collection_id')
        city = request.data.get('city')
        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')

        user = request.user

        collection = get_object_or_404(Collection, id=collection_id, owner=user)

        if item_type == 'Object':
            if city == 'AbuDhabi':
                item_model = Object_AbuDhabi
            elif city == 'Dubai':
                item_model = Object_Dubai
            else:
                return Response({"error": "Invalid city"}, status=status.HTTP_400_BAD_REQUEST)
        elif item_type == 'Unit':
            if city == 'AbuDhabi':
                item_model = Unit_AbuDhabi
            elif city == 'Dubai':
                item_model = Unit_Dubai
            else:
                return Response({"error": "Invalid city"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid item_type"}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(item_model, id=item_id)

        if item_model == Object_AbuDhabi:
            collection.objects_abudhabi.remove(item)
        elif item_model == Object_Dubai:
            collection.objects_dubai.remove(item)
        elif item_model == Unit_AbuDhabi:
            CollectionUnitsAbuDhabi.objects.filter(collection=collection, unit=item).delete()
        elif item_model == Unit_Dubai:
            CollectionUnitsDubai.objects.filter(collection=collection, unit=item).delete()

        return Response({"success": "Item removed from collection successfully"}, status=status.HTTP_200_OK)


class CollectionSetQuantityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'collection_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'city': openapi.Schema(type=openapi.TYPE_STRING),
                'unit_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            200: "Quantity set successfully",
        }
    )
    def post(self, request, *args, **kwargs):
        collection_id = request.data.get('collection_id')
        city = request.data.get('city')
        unit_id = request.data.get('unit_id')
        quantity = request.data.get('quantity')

        user = request.user

        collection = get_object_or_404(Collection, id=collection_id, owner=user)

        if city == 'AbuDhabi':
            item_model = Unit_AbuDhabi
        elif city == 'Dubai':
            item_model = Unit_Dubai
        else:
            return Response({"error": "Invalid city"}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(item_model, id=unit_id)

        if city == 'AbuDhabi':
            collection_unit = CollectionUnitsAbuDhabi.objects.filter(collection=collection, unit=item).first()
        elif city == 'Dubai':
            collection_unit = CollectionUnitsDubai.objects.filter(collection=collection, unit=item).first()

        if not collection_unit:
            return Response({"error": "Item not found in collection"}, status=status.HTTP_404_NOT_FOUND)

        collection_unit.quantity = quantity
        collection_unit.save()

        return Response({"success": "Quantity set successfully"}, status=status.HTTP_200_OK)


class CollectionDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'collection_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            204: "Collection deleted successfully",
        }
    )
    def post(self, request, *args, **kwargs):
        collection_id = request.data.get('collection_id')
        user = request.user
        collection = get_object_or_404(Collection, id=collection_id, owner=user)
        collection.delete()
        return Response({"success": "Collection deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CollectionCopyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'collection_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            201: "Collection copied successfully",
        }
    )
    def post(self, request, *args, **kwargs):
        collection_id = request.data.get('collection_id')
        user = request.user

        original_collection = get_object_or_404(Collection, id=collection_id, owner=user)
        copied_collection = Collection.objects.create(name=original_collection.name, owner=user)
        copied_collection.objects_abudhabi.add(*original_collection.objects_abudhabi.all())
        copied_collection.objects_dubai.add(*original_collection.objects_dubai.all())

        for collection_unit_abudhabi in original_collection.collectionunitsabudhabi_set.all():
            CollectionUnitsAbuDhabi.objects.create(collection=copied_collection, unit=collection_unit_abudhabi.unit, quantity=collection_unit_abudhabi.quantity)

        for collection_unit_dubai in original_collection.collectionunitsdubai_set.all():
            CollectionUnitsDubai.objects.create(collection=copied_collection, unit=collection_unit_dubai.unit, quantity=collection_unit_dubai.quantity)

        return Response({"success": "Collection copied successfully", "copied_collection_id": copied_collection.id}, status=status.HTTP_201_CREATED)


class BookingCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'passport_scan': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
                'units_abudhabi': openapi.Schema(type=openapi.TYPE_STRING),
                'units_dubai': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            201: "Bookings created successfully",
        }
    )
    def post(self, request, format=None):
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        passport_scan = request.data.get('passport_scan')
        units_abudhabi_ids = request.data.get('units_abudhabi', '').split(',')
        units_dubai_ids = request.data.get('units_dubai', '').split(',')

        if not units_abudhabi_ids and not units_dubai_ids:
            return Response({'error': 'Empty units_dubai and units_abudhabi'}, status=status.HTTP_400_BAD_REQUEST)

        for unit_id in units_abudhabi_ids:
            booking_data = {
                'full_name': full_name,
                'phone_number': phone_number,
                'email': email,
                'passport_scan': passport_scan,
                'units_abudhabi': [unit_id],
                'status': 'Pending'
            }
            serializer = BookingSerializer(data=booking_data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for unit_id in units_dubai_ids:
            booking_data = {
                'full_name': full_name,
                'phone_number': phone_number,
                'email': email,
                'passport_scan': passport_scan,
                'units_dubai': [unit_id],
                'status': 'Pending'
            }
            serializer = BookingSerializer(data=booking_data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        send_mail(
            'New booking'
            'Your booking has been created and sent',
            'gmorychev.work@gmail.com',
            [email],
            fail_silently=False,
        )

        return Response({'success': 'Bookings created successfully'}, status=status.HTTP_201_CREATED)


class UserBookingListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(owner=user)


class GetSharedCollectionView(APIView):
    def get(self, request, collection_id):
        collection = get_object_or_404(Collection, id=collection_id)
        if collection.is_shared:
            serializer = CollectionSerializer(collection)
            return JsonResponse(serializer.data)
        else:
            return JsonResponse({'message': 'This collection has not been shared.'}, status=403)


class ShareCollectionView(APIView):
    def post(self, request, collection_id):
        collection = get_object_or_404(Collection, id=collection_id)

        owner = collection.owner
        #owner = self.request.user

        owner_username = owner.username
        owner_email = owner.email

        collection.is_shared = True
        collection.save()

        send_collection_link(owner_username, owner_email, collection_id)

        return Response({"success": "Collection has been shared"}, status=status.HTTP_200_OK)


stripe.api_key = settings.STRIPE_SECRET_KEY


@swagger_auto_schema(method='post', request_body=PaymentSessionSerializer)
@api_view(['POST'])
def create_payment_session(request):
    serializer = PaymentSessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    subscription_id = serializer.validated_data['subscription_id']

    #subscription_id = request.data.get('subscription_type')

    subscription = get_object_or_404(Subscribtion, pk=subscription_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': subscription.name,
                },
                'unit_amount': subscription.price * 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://example.com/success/',
        cancel_url='https://example.com/cancel/',
    )

    return Response({'payment_url': session.url})