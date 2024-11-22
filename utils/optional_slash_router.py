from rest_framework.routers import SimpleRouter, DynamicRoute, Route


class OptionalSlashRouter(SimpleRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/simple{trailing_slash}$',
            mapping={
                'get': 'simple',
            },
            name='{basename}-simple',
            detail=False,
            initkwargs={'suffix': 'Simple'}
        ),
        # List route.
        # Route(
        #     url=r'^{prefix}/self{trailing_slash}$',
        #     mapping={
        #         'get': 'myself',
        #         'patch': 'myself_update',
        #     },
        #     name='{basename}-self',
        #     detail=False,
        #     initkwargs={'suffix': 'Self'}
        # ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
        # Update route.
        Route(
            url=r'^{prefix}/{lookup}/update{trailing_slash}$',
            mapping={
                'post': 'update'
            },
            name='{basename}-update',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Delete route.
        Route(
            url=r'^{prefix}/{lookup}/delete{trailing_slash}$',
            mapping={
                'post': 'destroy'
            },
            name='{basename}-delete',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Delete route.
        Route(
            url=r'^{prefix}/{lookup}/delete/multiple{trailing_slash}$',
            mapping={
                'post': 'multiple_delete'
            },
            name='{basename}-multiple_delete',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
    ]

    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'
