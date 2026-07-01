from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProjectOwner(BasePermission):
    """
    DELETE — только владелец
    GET / PUT / PATCH — владелец и участник
    """

    def has_object_permission(self, request, view, obj):

        # владелец всегда проходит
        if obj.owner == request.user:
            return True

        # участник может читать и менять, но не удалять
        if request.method in SAFE_METHODS:
            return obj.is_member(request.user)

        if request.method in ("PUT", "PATCH"):
            return obj.is_member(request.user)

        # DELETE — только владелец
        if request.method == "DELETE":
            return obj.owner == request.user

        return False

class IsProjectMember(BasePermission):
    """
    Доступ к проекту только владельцу и участникам.
    """

    def has_object_permission(self, request, view, obj):
        return obj.is_member(request.user)


class IsTaskProjectMember(BasePermission):
    """
    Доступ к задачам только участникам проекта.
    """

    def has_object_permission(self, request, view, obj):
        return obj.project.is_member(request.user)


class IsCommentProjectMember(BasePermission):
    """
    Читать комментарии могут участники проекта.
    Изменять и удалять комментарий может только его автор.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.task.project.is_member(request.user)

        return obj.author == request.user


class IsProjectOwnerOrMember(BasePermission):
    """
    Владелец и участники имеют доступ к проекту.
    """

    def has_object_permission(self, request, view, obj):
        return obj.is_member(request.user)