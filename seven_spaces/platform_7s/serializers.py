from decimal import Decimal

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from platform_7s.models import Applications, Object_Dubai, Object_AbuDhabi, Unit_Dubai, Unit_AbuDhabi, Collection, \
    Booking, Subscribtion


class ApplicationsSerializer(ModelSerializer):
    class Meta:
        model = Applications
        fields = '__all__'


class ObjectDubaiSerializer(ModelSerializer):
    class Meta:
        model = Object_Dubai
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and 'X-Wallet' in request.headers:
            wallet_currency = request.headers['X-Wallet']
            if wallet_currency == 'USD':
                if instance.overall_min_unit_price is not None:
                    instance.overall_min_unit_price /= Decimal('3.65')
                if instance.overall_max_unit_price is not None:
                    instance.overall_max_unit_price /= Decimal('3.65')
                if instance.overall_min_unit_psf is not None:
                    instance.overall_min_unit_psf /= Decimal('3.65')
                if instance.overall_max_unit_psf is not None:
                    instance.overall_max_unit_psf /= Decimal('3.65')
                if instance.down_price is not None:
                    instance.down_price /= Decimal('3.65')
                if instance.total:
                    if 'sumMax' in instance.total:
                        instance.total['sumMax'] /= 3.65
                    if 'sumMin' in instance.total:
                        instance.total['sumMin'] /= 3.65
                if instance.apartments:
                    for el in instance.apartments:
                        instance.apartments[el]['sumMin'] /= 3.65
        return super().to_representation(instance)


class ObjectAbuDhabiSerializer(ModelSerializer):
    class Meta:
        model = Object_AbuDhabi
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and 'X-Wallet' in request.headers:
            wallet_currency = request.headers['X-Wallet']
            if wallet_currency == 'USD':
                if instance.overall_min_unit_price is not None:
                    instance.overall_min_unit_price /= Decimal('3.65')
                if instance.overall_max_unit_price is not None:
                    instance.overall_max_unit_price /= Decimal('3.65')
                if instance.overall_min_unit_psf is not None:
                    instance.overall_min_unit_psf /= Decimal('3.65')
                if instance.overall_max_unit_psf is not None:
                    instance.overall_max_unit_psf /= Decimal('3.65')
                if instance.down_price is not None:
                    instance.down_price /= Decimal('3.65')
                if instance.total:
                    if 'sumMax' in instance.total:
                        instance.total['sumMax'] /= 3.65
                    if 'sumMin' in instance.total:
                        instance.total['sumMin'] /= 3.65
                if instance.apartments:
                    for el in instance.apartments:
                        instance.apartments[el]['sumMin'] /= 3.65
        return super().to_representation(instance)


class UnitDubaiSerializer(ModelSerializer):
    class Meta:
        model = Unit_Dubai
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and 'X-Wallet' in request.headers:
            wallet_currency = request.headers['X-Wallet']
            if wallet_currency == 'USD':
                if instance.price_min is not None:
                    instance.price_min /= Decimal('3.65')
                if instance.price_max is not None:
                    instance.price_max /= Decimal('3.65')
                if instance.psf_min is not None:
                    instance.psf_min /= Decimal('3.65')
                if instance.psf_max is not None:
                    instance.psf_max /= Decimal('3.65')
        return super().to_representation(instance)


class UnitAbuDhabiSerializer(ModelSerializer):
    class Meta:
        model = Unit_AbuDhabi
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and 'X-Wallet' in request.headers:
            wallet_currency = request.headers['X-Wallet']
            if wallet_currency == 'USD':
                if instance.price_min is not None:
                    instance.price_min /= Decimal('3.65')
                if instance.price_max is not None:
                    instance.price_max /= Decimal('3.65')
                if instance.psf_min is not None:
                    instance.psf_min /= Decimal('3.65')
                if instance.psf_max is not None:
                    instance.psf_max /= Decimal('3.65')
        return super().to_representation(instance)


class CollectionSerializer(ModelSerializer):
    units_abudhabi = SerializerMethodField()
    units_dubai = SerializerMethodField()

    class Meta:
        model = Collection
        fields = ('id', 'name', 'owner', 'objects_abudhabi', 'objects_dubai', 'units_abudhabi', 'units_dubai')

    def get_units_abudhabi(self, obj):
        units = obj.collectionunitsabudhabi_set.all()
        return [{'id': unit.unit.id, 'quantity': unit.quantity} for unit in units]

    def get_units_dubai(self, obj):
        units = obj.collectionunitsdubai_set.all()
        return [{'id': unit.unit.id, 'quantity': unit.quantity} for unit in units]


class CollectionCreateSerializer(ModelSerializer):
    class Meta:
        model = Collection
        fields = ['name']

    def create(self, validated_data):
        user = self.context['request'].user
        collection = Collection.objects.create(owner=user, **validated_data)
        collection.objects_abudhabi.set([])
        collection.objects_dubai.set([])
        return collection


class BookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'full_name', 'phone_number', 'email', 'passport_scan', 'units_abudhabi', 'units_dubai',
                  'status']

    def create(self, validated_data):
        units_abudhabi_data = validated_data.pop('units_abudhabi', [])
        units_dubai_data = validated_data.pop('units_dubai', [])

        booking = Booking.objects.create(**validated_data)

        for unit_id in units_abudhabi_data:
            unit = Unit_AbuDhabi.objects.get(id=unit_id)
            booking.units_abudhabi.add(unit)

        for unit_id in units_dubai_data:
            unit = Unit_Dubai.objects.get(id=unit_id)
            booking.units_dubai.add(unit)

        return booking


class SubscribtionSerializer(ModelSerializer):
    class Meta:
        model = Subscribtion
        fields = '__all__'


class PaymentSessionSerializer(Serializer):
    subscription_id = serializers.IntegerField()