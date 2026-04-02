from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from core.permissions import IsAdmin, IsAnyRole
from .models import Transaction
from .serializers import TransactionSerializer, TransactionCreateUpdateSerializer


class TransactionListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAnyRole()]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        # Filtering
        t = request.query_params.get('type')
        category = request.query_params.get('category')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')

        if t:
            qs = qs.filter(type=t)
        if category:
            qs = qs.filter(category=category)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAnyRole()]
        return [IsAdmin()]

    def get_object(self, pk):
        try:
            return Transaction.objects.get(pk=pk, is_deleted=False)
        except Transaction.DoesNotExist:
            return None

    def get(self, request, pk):
        transaction = self.get_object(pk)
        if not transaction:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TransactionSerializer(transaction).data)

    def put(self, request, pk):
        transaction = self.get_object(pk)
        if not transaction:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionCreateUpdateSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(TransactionSerializer(transaction).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        transaction = self.get_object(pk)
        if not transaction:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionCreateUpdateSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(TransactionSerializer(transaction).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        transaction = self.get_object(pk)
        if not transaction:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        transaction.is_deleted = True  # soft delete
        transaction.save()
        return Response({'detail': 'Transaction deleted.'}, status=status.HTTP_204_NO_CONTENT)