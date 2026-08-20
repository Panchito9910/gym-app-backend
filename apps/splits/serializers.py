"""Splits serializers."""
from rest_framework import serializers

from .models import Split, SplitDay, UserSplit


class SplitDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SplitDay
        fields = ['id', 'idSplit', 'dayNumber', 'name', 'status', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']


class SplitSerializer(serializers.ModelSerializer):
    days = SplitDaySerializer(many=True, read_only=True)

    class Meta:
        model = Split
        fields = ['id', 'name', 'description', 'status', 'created', 'updated', 'days']
        read_only_fields = ['id', 'created', 'updated']


class UserSplitSerializer(serializers.ModelSerializer):
    splitName = serializers.CharField(source='idSplit.name', read_only=True)

    class Meta:
        model = UserSplit
        fields = [
            'id',
            'idUser',
            'idSplit',
            'splitName',
            'startDate',
            'endDate',
            'isActive',
            'status',
            'created',
            'updated',
        ]
        read_only_fields = ['id', 'idUser', 'created', 'updated', 'splitName']

    def validate(self, attrs):
        end = attrs.get('endDate')
        start = attrs.get('startDate') or getattr(self.instance, 'startDate', None)
        if end and start and end < start:
            raise serializers.ValidationError({'endDate': 'endDate must be after startDate.'})
        return attrs
