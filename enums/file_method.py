from utils import ChoiceEnum


class FileStorageMethod(ChoiceEnum):
    """文件存储方式"""
    Local = 0
    """本地存储"""
    AliCloud = 1
    """阿里云"""
