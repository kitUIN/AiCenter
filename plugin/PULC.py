from .plugin_tool import BasePlugin, plugin_template, StartupData, ArgData


@plugin_template
class PULCPlugin(BasePlugin):
    _key = "PULC"
    _info = "超轻量图像分类"
    """说明"""
    _icon = "pp.png"
    """图标"""

    def get_startup(self, *args, **kwargs) -> StartupData:
        return StartupData(
            value="""python3 -m paddle.distributed.launch --gpus="{gpus}" tools/train.py -c {config}""",
            allow_modify=True
        )

    def get_args(self, *args, **kwargs) -> list[ArgData]:
        return [
            ArgData(id=1, name="gpus", value="0", type="string", info="使用的GPU,逗号分隔"),
            ArgData(id=2, name="config", value="", type="file", info="配置文件所在位置"),
        ]
