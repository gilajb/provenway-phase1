from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .ratelimiting import enforce_leads_rate_limit
from .serializers import InterestSignupSerializer


class InterestSignupCreateView(APIView):
    """POST /api/v1/leads/interest/ — public lead capture for the
    "For Construction Firms" and "Educational Access" marketing pages.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        enforce_leads_rate_limit(request, group="leads_interest")
        serializer = InterestSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Honeypot tripped: return the same success response a real
        # visitor gets, but silently drop the submission — telling a bot
        # it failed only teaches it to adapt.
        if serializer.validated_data.get("website"):
            return Response(status=status.HTTP_201_CREATED)

        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
