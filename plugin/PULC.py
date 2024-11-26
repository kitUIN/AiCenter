from .plugin_tool import BasePlugin, plugin_template, StartupData, ArgData


@plugin_template
class PULCPlugin(BasePlugin):
    _key = "PULC"
    _info = "飞浆超轻量图像分类"
    """说明"""
    _icon = "pp"
    """图标"""
    def get_startup(self, *args, **kwargs) -> StartupData:
        return StartupData(
            value="""python3 -m paddle.distributed.launch \
    --gpus="{gpus}" \
    tools/train.py \
    -c {config}""",
            allow_modify=True
        )

    def get_args(self, *args, **kwargs) -> list[ArgData]:
        return [
            ArgData(name="gpus", value="0", info="使用的GPU,逗号分隔"),
            ArgData(name="config", value="", info="配置文件所在位置"),
        ]
