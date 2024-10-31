from rest_framework.response import Response


class ListResponse(Response):
    """分页响应成功的返回"""

    def __init__(self, data=None, msg='success', status=None, template_name=None, headers=None, exception=False,
                 content_type='application/json; charset=utf-8', page=1, limit=1, total=1):
        std_data = {
            "code": 200,
            "data": {
                "page": page,
                "limit": limit,
                "total": total,
                "data": data
            },
            "msg": msg
        }
        super().__init__(std_data, status, template_name, headers, exception, content_type)


class DetailResponse(Response):
    """不包含分页信息的接口返回,主要用于单条数据查询"""

    def __init__(self, data=None, msg='success', status=None, template_name=None, headers=None, exception=False,
                 content_type='application/json; charset=utf-8'):
        std_data = {
            "code": 200,
            "data": data,
            "msg": msg
        }
        super().__init__(std_data, status, template_name, headers, exception, content_type)


class ErrorResponse(Response):
    """标准响应错误的返回"""

    def __init__(self, data=None, msg='error', code=400, status=None, template_name=None, headers=None,
                 exception=False, content_type='application/json; charset=utf-8'):
        std_data = {
            "code": code,
            "data": data,
            "msg": msg
        }
        super().__init__(std_data, status, template_name, headers, exception, content_type)
