from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.ratelimiting import enforce_rate_limit

from .models import VerificationCredential
from .serializers import CredentialSerializer, CredentialSubmitSerializer
from .service.cloudinary_service import CloudinaryUploadError, upload_credential_document


class CredentialSubmitView(APIView):
    """POST /api/v1/credentials/ — submit a credential document for
    admin review (Engineering Doc §1.4.7).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Infrequent/serious action — a generous daily cap just bounds
        # abuse, not real usage (nobody submits credentials dozens of
        # times a day).
        enforce_rate_limit(request, group="credential_submit", rate="10/d")
        serializer = CredentialSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.validated_data["document"]
        document_type = serializer.validated_data["document_type"]

        try:
            upload_result = upload_credential_document(
                document, user_id=str(request.user.id), document_type=document_type
            )
        except CloudinaryUploadError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        credential = VerificationCredential.objects.create(
            user=request.user,
            document_type=document_type,
            document_url=upload_result["secure_url"],
        )
        return Response(
            CredentialSerializer(credential).data, status=status.HTTP_201_CREATED
        )


class CredentialMeView(APIView):
    """GET /api/v1/credentials/me/ — the requester's own submissions,
    newest first (a user may resubmit after rejection or submit multiple
    document types).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        credentials = VerificationCredential.objects.filter(user=request.user)
        return Response(CredentialSerializer(credentials, many=True).data)
