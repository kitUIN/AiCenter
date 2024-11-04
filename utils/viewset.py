from typing import List, Optional

from django.db.models import QuerySet
from django_restql.mixins import QueryArgumentsMixin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from enums.viewset_method import ViewSetRequestMethod
from .json_response import ListResponse, ErrorResponse, DetailResponse


class CustomModelViewSet(ModelViewSet, QueryArgumentsMixin):
    """
    自定义的ModelViewSet:
    统一标准的返回格式;新增,查询,修改可使用不同序列化器
    (1)ORM性能优化, 尽可能使用values_queryset形式
    (2)xxx_serializer_class 某个方法下使用的序列化器(xxx=create|update|list|retrieve|destroy)
    (3)filter_fields = '__all__' 默认支持全部model中的字段查询(除json字段外)
    """
    extra_lookup_fields = {}
    """额外筛选"""
    values_queryset: Optional[QuerySet] = None
    """queryset"""
    ordering_fields = '__all__'
    """排序字段"""
    list_serializer_class = None
    create_serializer_class = None
    retrieve_serializer_class = None
    update_serializer_class = None
    filter_fields = '__all__'
    search_fields = ()
    exclude_methods: List[ViewSetRequestMethod] = []
    """排除的接口,self.action"""
    extra_filter_backends = []
    """过滤"""
    permission_classes = []
    """权限"""

    def check_exclude_methods(self, request: Request, *args, **kwargs):
        return self.action in [j.value for j in self.exclude_methods]

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        if self.extra_lookup_fields:
            filter_kwargs = {k: self.kwargs[v] for k, v in self.extra_lookup_fields.items()}

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        for backend in set(set(self.filter_backends) | set(self.extra_filter_backends or [])):
            # print(backend)
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            return self.values_queryset
        return super().get_queryset()

    def get_serializer_class(self, other: str = None):
        action_serializer_name = f"{self.action}_{f'{other}_' if other else ''}serializer_class"
        # print(action_serializer_name)
        action_serializer_class = getattr(self, action_serializer_name, None)
        if action_serializer_class:
            return action_serializer_class
        return super().get_serializer_class()

    # 通过many=True直接改造原有的API，使其可以批量创建
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if isinstance(self.request.data, list):
            return serializer_class(many=True, *args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    def create(self, request: Request, *args, **kwargs):
        """新增"""
        if self.check_exclude_methods(request, *args, **kwargs):
            return ErrorResponse(msg="接口未开放", code=404)
        data = request.data.copy()
        # if request.user and request.user.is_tenant:
        #     if isinstance(data, list):
        #         for i in data:
        #             i["tenant"] = request.user.tenant.id
        #     else:
        #         data["tenant"] = request.user.tenant.id
        serializer = self.get_serializer(data=data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DetailResponse(data=serializer.data, msg="新增成功")

    def list(self, request: Request, *args, **kwargs):
        """列表"""
        if self.check_exclude_methods(request, *args, **kwargs):
            return ErrorResponse(msg="接口未开放", code=404)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return ListResponse(data=serializer.data, msg="获取成功")

    def retrieve(self, request: Request, *args, **kwargs):
        """详细"""
        if self.check_exclude_methods(request, *args, **kwargs):
            return ErrorResponse(msg="接口未开放", code=404)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return DetailResponse(data=serializer.data, msg="获取成功")

    def update(self, request: Request, *args, **kwargs):
        """更新"""
        if self.check_exclude_methods(request, *args, **kwargs):
            return ErrorResponse(msg="接口未开放", code=404)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, request=request, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return DetailResponse(data=serializer.data, msg="更新成功")

    def destroy(self, request: Request, *args, **kwargs):
        """单个删除"""
        if self.check_exclude_methods(request, *args, **kwargs):
            return ErrorResponse(msg="接口未开放", code=404)
        instance = self.get_object()
        instance.delete()
        return DetailResponse(data=[], msg="删除成功")

    def multiple_delete(self, request, *args, **kwargs):
        """批量删除"""
        request_data = request.data
        keys = request_data.get('keys', None)
        if keys:
            self.get_queryset().filter(id__in=keys).delete()
            return ListResponse(data=[], msg="删除成功")
        else:
            return ErrorResponse(msg="未获取到keys字段")


__all__ = [
    "CustomModelViewSet"
]
