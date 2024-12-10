import cv2
import numpy as np
from paddleclas.deploy.python.postprocess import build_postprocess
from paddleclas.deploy.python.preprocess import create_operators
from paddleclas.deploy.utils import logger
from paddleclas.deploy.utils.config import get_config
from paddleclas.deploy.utils.predictor import Predictor
from rest_framework.response import Response

from utils import DetailResponse, ErrorResponse
from .plugin_tool import BasePlugin, plugin_template, StartupData, ArgData, TaskStepData, PredictFile


class ClsPredictor(Predictor):
    def __init__(self, config):
        super().__init__(config["Global"])

        self.preprocess_ops = []
        self.postprocess = None
        if "PreProcess" in config:
            if "transform_ops" in config["PreProcess"]:
                self.preprocess_ops = create_operators(config["PreProcess"][
                                                           "transform_ops"])
        if "PostProcess" in config:
            self.postprocess = build_postprocess(config["PostProcess"])

        # for whole_chain project to test each repo of paddle
        self.benchmark = config["Global"].get("benchmark", False)
        if self.benchmark:
            import auto_log
            import os
            pid = os.getpid()
            size = config["PreProcess"]["transform_ops"][1]["CropImage"][
                "size"]
            if config["Global"].get("use_int8", False):
                precision = "int8"
            elif config["Global"].get("use_fp16", False):
                precision = "fp16"
            else:
                precision = "fp32"
            self.auto_logger = auto_log.AutoLogger(
                model_name=config["Global"].get("model_name", "cls"),
                model_precision=precision,
                batch_size=config["Global"].get("batch_size", 1),
                data_shape=[3, size, size],
                save_path=config["Global"].get("save_log_path",
                                               "./auto_log.log"),
                inference_config=self.config,
                pids=pid,
                process_name=None,
                gpu_ids=None,
                time_keys=[
                    'preprocess_time', 'inference_time', 'postprocess_time'
                ],
                warmup=2)

    def predict(self, images):
        use_onnx = self.args.get("use_onnx", False)
        if not use_onnx:
            input_names = self.predictor.get_input_names()
            input_tensor = self.predictor.get_input_handle(input_names[0])

            output_names = self.predictor.get_output_names()
            output_tensor = self.predictor.get_output_handle(output_names[0])
        else:
            input_names = self.predictor.get_inputs()[0].name
            output_names = self.predictor.get_outputs()[0].name

        if self.benchmark:
            self.auto_logger.times.start()
        if not isinstance(images, (list,)):
            images = [images]
        for idx in range(len(images)):
            for ops in self.preprocess_ops:
                images[idx] = ops(images[idx])
        image = np.array(images)
        if self.benchmark:
            self.auto_logger.times.stamp()

        if not use_onnx:
            input_tensor.copy_from_cpu(image)
            self.predictor.run()
            batch_output = output_tensor.copy_to_cpu()
        else:
            batch_output = self.predictor.run(
                output_names=[output_names],
                input_feed={input_names: image})[0]

        if self.benchmark:
            self.auto_logger.times.stamp()
        if self.postprocess is not None:
            batch_output = self.postprocess(batch_output)
        if self.benchmark:
            self.auto_logger.times.end(stamp=True)
        return batch_output


@plugin_template
class PULCPlugin(BasePlugin):
    _key = "PULC"
    _info = "超轻量图像分类"
    """说明"""
    _icon = "pp.png"
    """图标"""

    def get_startup(self, *args, **kwargs) -> StartupData:
        return StartupData(
            value="""
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
""",
            allow_modify=True
        )

    def get_args(self, *args, **kwargs) -> list[ArgData]:
        return [
            ArgData(id=1, name="gpus", value="0", type="string", info="使用的GPU,逗号分隔"),
            ArgData(id=2, name="config", value="", type="file", info="配置文件所在位置"),
        ]

    def get_task_steps(self, requirements, startup_cmd, *args, **kwargs) -> list[TaskStepData]:
        return [
            # TaskStepData(name="创建虚拟环境", cmd="", step_type="venv"),
            # TaskStepData(name="安装依赖", cmd=f"pip install -r {requirements}", step_type="normal"),
            # TaskStepData(name="安装paddlepaddle", cmd="python -m pip install paddlepaddle-gpu==3.0.0b2 -i "
            #                                           "https://www.paddlepaddle.org.cn/packages/stable/cu123/",
            #              step_type="normal"),
            TaskStepData(name="下载PaddleClas环境", cmd=r"mklink /j PaddleClas D:\PaddleClas",
                         step_type="normal"),
            TaskStepData(name="开始训练", cmd=f"cd PaddleClas && {startup_cmd}", step_type="normal"),
        ]

    def _predict_image(self, image: list[PredictFile]) -> Response:
        config = get_config("./plugin/inference_traffic_sign.yaml", show=True)
        cls_predictor = ClsPredictor(config)
        batch_imgs = []
        batch_names = []
        cnt = 0

        res = []
        for idx, image_c in enumerate(image):
            nparr = np.frombuffer(image_c.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                logger.warning(
                    "Image file failed to read and has been skipped. The path: {}".
                    format(image_c.name))
            else:
                img = img[:, :, ::-1]
                batch_imgs.append(img)
                batch_names.append(image_c.name)
                cnt += 1

        batch_results = cls_predictor.predict(batch_imgs)
        for number, result_dict in enumerate(batch_results):
            filename = batch_names[number]
            # print("{}:\t {}".format(filename, result_dict))
            if "scores" in result_dict.keys():
                result_dict["scores"] = [round(i, 3) for i in result_dict["scores"]]
            res.append({"filename": filename, "result": result_dict})
        if res:
            return DetailResponse(data=res, msg="查询成功")
        return ErrorResponse(msg="无结果")
