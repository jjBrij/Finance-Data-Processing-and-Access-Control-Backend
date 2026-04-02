from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'type', 'category',
            'date', 'notes', 'created_by',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'is_deleted', 'created_at', 'updated_at']


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'category', 'date', 'notes']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value