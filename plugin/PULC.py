import json
from pathlib import Path

import cv2
import numpy as np
from paddleclas.deploy.python.postprocess import build_postprocess
from paddleclas.deploy.python.preprocess import create_operators
from paddleclas.deploy.utils import logger
from paddleclas.deploy.utils.config import get_config
from paddleclas.deploy.utils.predictor import Predictor
from rest_framework.request import Request
from rest_framework.response import Response

from center.models.workflow import AiModelPower, TrainTask
from utils import DetailResponse, ErrorResponse
from utils.jenkins import get_jenkins_manager
from .plugin_tool import BasePlugin, plugin_template, StartupData, ArgData, TaskStepData, PredictFile, ApiDocData, \
    ApiDocArgData


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
            value="""pipeline {
    agent any
    environment {
#CUSTOM_ENV_ARGS#
    }
    stages {
        stage('虚拟环境') {
            steps {
                script {
                    sh 'mkdir -p ${WORKSPACE}/result'
                    sh 'mkdir -p ${WORKSPACE}/model'
                    bat 'D:/PycharmProjects/AiCenter/.venv/Scripts/activate.bat'
                }
            }
        }
        stage('训练模型') {
            steps {
                script {
                    bat \"\"\"
                    cd D:/PaddleClas
                    python -m paddle.distributed.launch --gpus="0" tools/train.py -c ${TRAIN_MODEL_CONFIG_FILE} -o Global.output_dir=${WORKSPACE}/result -o Global.save_inference_dir=${WORKSPACE}/result
                    \"\"\"
                }
            }
        }
        stage('导出模型') {
            steps {
                script {
                    bat \"\"\"
                    cd D:/PaddleClas
                    python tools/export_model.py -c ${EXPORT_MODEL_CONFIG_FILE} -o Global.pretrained_model=${WORKSPACE}/result/best_model -o Global.save_inference_dir=${WORKSPACE}/model
                    \"\"\"
                    archiveArtifacts artifacts: 'model/**', followSymlinks: false
                }
            }
        }
    }
}""",
            allow_modify=True
        )
    def get_startup_args(self, *args, **kwargs) -> list[ArgData]:
        return [
            # ./ppcls/configs/PULC/traffic_sign/PPLCNet_x1_0.yaml
            ArgData(id=0, name="TRAIN_MODEL_CONFIG_FILE", value=None, type="file", required=False, info="模型训练配置文件"),
            # ./ppcls/configs/PULC/traffic_sign/PPLCNet_x1_0.yaml
            ArgData(id=1, name="EXPORT_MODEL_CONFIG_FILE",
                    value="", required=True, type="file", info="模型导出配置文件"),
        ]
    def get_power_args(self, *args, **kwargs) -> list[ArgData]:
        return [
            ArgData(id=0, name="config",
                    value="", required=True, type="file", info="模型配置文件"),
            ArgData(id=1, name="class_id_map_file", value=None, type="file", required=False, info="模型分类标签文件"),
            ArgData(id=2, name="inference_model_dir", value=None, type="file", info="预测模型所在文件夹"),
        ]

    def _predict_image(self, request: Request, image: list[PredictFile], power: AiModelPower, kwargs: dict) -> Response:
        overrides = []
        class_id_map_file = kwargs.get("class_id_map_file")
        inference_model_dir = kwargs.get("inference_model_dir",
                                         Path(f"artifact/{power.task.plan.name}/{power.task.number}/model"))
        if inference_model_dir:
            overrides.append(f"Global.inference_model_dir={inference_model_dir}")
        if class_id_map_file:
            overrides.append(f"PostProcess.TopK.class_id_map_file={class_id_map_file}")
        config = get_config(kwargs.get("config"), show=True, overrides=overrides)
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

    def get_api_doc(self, *args, **kwargs) -> ApiDocData:
        return ApiDocData(name="预测", description="使用模型进行预测分析",
                          method="POST", content_type="multipart/form-data", api="/predict",
                          request_body=[
                              ApiDocArgData(
                                  name="file",
                                  arg_type="File",
                                  description="需要进行预测分析的图片",
                                  required=True)
                          ],
                          response_body=[
                              ApiDocArgData(
                                  name="code",
                                  arg_type="int",
                                  description="状态码,200为成功",
                                  required=True),
                              ApiDocArgData(
                                  name="msg",
                                  arg_type="string",
                                  description="返回说明",
                                  required=True),
                              ApiDocArgData(
                                  name="data",
                                  arg_type="object",
                                  description="仅成功时返回",
                                  children=[
                                      ApiDocArgData(
                                          name="score",
                                          arg_type="double",
                                          description="识别分数",
                                          required=True),
                                  ]
                              ),
                          ])
