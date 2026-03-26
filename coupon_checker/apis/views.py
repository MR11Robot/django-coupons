from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..models import Country, Coupon, Website, Store, CouponReport
from .serializers import CouponSerializer, WebsiteSerializer, StoreSerializer, CouponReportSerializer
from ..permissions import HasCouponCheckerAPIKey
from ..pagination import StandardResultsSetPagination
from django.core.exceptions import ValidationError

# Website List View
class WebsiteListView(APIView):
    permission_classes = [HasCouponCheckerAPIKey | IsAuthenticated]

    def get(self, request):
        websites = Website.objects.all().order_by('updated_at')
        serializer = WebsiteSerializer(websites, many=True)
        return Response(serializer.data)


# Store List View (Requires website_slug)
class StoreListView(APIView):
    permission_classes = [HasCouponCheckerAPIKey | IsAuthenticated]

    def get(self, request, website_slug):
        website = get_object_or_404(Website, slug=website_slug)
        stores = Store.objects.filter(website=website).order_by('updated_at')
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


# Coupon List View
class CouponListView(APIView):
    permission_classes = [HasCouponCheckerAPIKey | IsAuthenticated]


    def get(self, request):
        coupons = Coupon.objects.all().order_by('updated_at')
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)


# Store Coupons View (Nested route)
class StoreCouponsView(APIView):
    permission_classes = [HasCouponCheckerAPIKey | IsAuthenticated]

    def get(self, request, store_slug):
        stores = Store.objects.filter(slug=store_slug)
        coupons = Coupon.objects.filter(store__in=stores).order_by('updated_at')
        serializer = CouponSerializer(coupons, many=True)
        return Response({'coupons': serializer.data})


# Coupon Report View (GET + POST)
class CouponReportListView(APIView):
    permission_classes = [HasCouponCheckerAPIKey | IsAuthenticated]

    def get(self, request):
        reports = CouponReport.objects.all().order_by('last_check')
        serializer = CouponReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CouponReportSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except ValidationError as e:
                return Response({'error': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
