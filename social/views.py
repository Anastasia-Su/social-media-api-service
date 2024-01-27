from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Post
from .permissions import IsAdminOrIfAuthenticatedReadOnly
from .serializers import PostSerializer, PostListSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


