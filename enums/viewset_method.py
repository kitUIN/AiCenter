from utils import ChoiceEnum


class ViewSetRequestMethod(ChoiceEnum):
    """ViewSet自带的几种请求"""
    List = "list"
    """列表"""
    Retrieve = "retrieve"
    """详细"""
    Create = "create"
    """创建"""
    Update = "update"
    """更新"""
    Destroy = "destroy"
    """删除"""
    Simple = "simple"
    """简单"""
