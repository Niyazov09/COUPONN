from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProjectOwner(BasePermission):
    """
    Только владелец проекта может удалять проект.
    Владелец и участники могут просматривать и изменять проект.
    """

    def has_object_permission(self, request, view, obj):
        # Просмотр — владелец и участники
        if request.method in SAFE_METHODS:
            return obj.is_member(request.user)

        # PATCH / PUT — владелец и участники
        if request.method in ("PUT", "PATCH"):
            return obj.is_member(request.user)

        # DELETE — только владелец
        return obj.owner == request.user


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