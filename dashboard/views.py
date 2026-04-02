from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncWeek
from core.permissions import IsAnyRole
from transactions.models import Transaction


class SummaryView(APIView):
    """Total income, expenses, and net balance."""
    permission_classes = [IsAnyRole]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        total_income = qs.filter(type='income').aggregate(
            total=Sum('amount'))['total'] or 0

        total_expense = qs.filter(type='expense').aggregate(
            total=Sum('amount'))['total'] or 0

        net_balance = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
        })


class CategorySummaryView(APIView):
    """Total amount grouped by category."""
    permission_classes = [IsAnyRole]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        by_category = (
            qs.values('category', 'type')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('category')
        )

        return Response(list(by_category))


class MonthlyTrendsView(APIView):
    """Income and expense totals grouped by month."""
    permission_classes = [IsAnyRole]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        monthly = (
            qs.annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Format into clean structure
        result = {}
        for entry in monthly:
            month_str = entry['month'].strftime('%Y-%m')
            if month_str not in result:
                result[month_str] = {'month': month_str, 'income': 0, 'expense': 0}
            result[month_str][entry['type']] = entry['total']

        return Response(list(result.values()))


class RecentActivityView(APIView):
    """Last 10 transactions."""
    permission_classes = [IsAnyRole]

    def get(self, request):
        from transactions.serializers import TransactionSerializer
        qs = Transaction.objects.filter(is_deleted=False).order_by('-created_at')[:10]
        from transactions.serializers import TransactionSerializer
        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data)