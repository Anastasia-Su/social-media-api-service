from rest_framework import status
from rest_framework.response import Response


class ToggleFollowMixin:
    def toggle_follow_common(self, request, instance):
        profile = instance.user.profile

        if request.method == "POST" and request.user.profile != profile:
            follow_status = request.data.get("follow", "")
            if follow_status == "U":
                profile.followers.remove(request.user)
                request.user.profile.is_following.remove(profile.user)
            if follow_status == "F":
                profile.followers.add(request.user)
                request.user.profile.is_following.add(profile.user)

            profile.save()

            serializer = self.get_serializer(instance=profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)


class ToggleLikeMixin:
    def toggle_like_common(self, request, post):
        if request.method == "POST" and request.user.profile != post.user.profile:
            like_status = request.data.get("like", "")
            if like_status == "U":
                post.liked_by.remove(request.user)
                request.user.profile.i_like.remove(post)
            if like_status in ["L", "D"]:
                post.liked_by.add(request.user)
                request.user.profile.i_like.add(post)

            post.save()

            serializer = self.get_serializer(instance=post, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)
