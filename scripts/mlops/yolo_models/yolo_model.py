import os
import torch
import numpy as np
from mlserver.codecs import decode_args
from mlserver import MLModel, types
from typing import List
import pandas as pd
import mlflow

import redis

import logging

logging.basicConfig(level=logging.DEBUG)




class MyYOLOModel(MLModel):
    
    async def load(self) -> bool:
        # env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        # mlflow.set_tracking_uri(uri=env.get('mlflow_tracking_uri'))
        # mlflow.set_experiment(env.get("experiment_log_yolo"))
        # self.model_uri = env.get("yolov5s_model_uri")
        # Load the model (use the appropriate YOLO version, here it's YOLOv5m)
        self.models = {}
        self.models['few_shot'] = torch.hub.load("ultralytics/yolov5", "custom", path="./models/few_shot.pt", force_reload=False)
        self.models['fine_tune'] = torch.hub.load("ultralytics/yolov5", "custom", path="./models/fine_tune.pt", force_reload=False)
        self.models['yolov5m'] = torch.hub.load("ultralytics/yolov5", "custom", path="./models/yolov5m.pt", force_reload=False)
        self.models['yolov5s'] = torch.hub.load("ultralytics/yolov5", "custom", path="./models/yolov5s.pt", force_reload=False)
        self.env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

        # self.model = mlflow.pyfunc.load_model(model_uri=self.model_uri)
        return True
    
    async def predict(self, payload: types.InferenceRequest) -> types.InferenceResponse:
        # print(type(image))
        # logging.critical(f"This will get logged. {type()}")
        # Perform inference on the image
        image = self.decode(payload.inputs[0])
        model = self.env.get('model')
        results = self.models[model](image)
        df = results.pandas().xyxy[0]  # Get the pandas DataFrame of the results

        # Filter detections for persons (class 0) with confidence > 0.85
        person_detections = df[(df["class"] == 0) & (df["confidence"] > 0.85)]

        conf = str(df[df["class"] == 0]['confidence'].max())
        # Determine if any person was detected
        if not person_detections.empty:
            response_data = 'true'  # Or use 1 if you prefer integers
        else:
            response_data = 'false'  # Or use 0 if you prefer integers

        
        # Prepare the response
        response_bytes = response_data.encode("utf-8")  # Convert response to bytes
        conf_bytes = conf.encode("utf-8")
        
        # Create an InferenceResponse
        response = types.InferenceResponse(
            model_name=self.name,
            model_version=self.version,
            outputs=[
                types.ResponseOutput(
                    name="detection_status",  # Name of the output field
                    shape=[len(response_bytes), len(conf_bytes)],  # Shape of the output (should match length of bytes)
                    datatype="BYTES",  # Data type of the output
                    data=[response_bytes,conf_bytes],  # Encoded response data
                    parameters=types.Parameters(content_type="str"),  # Ensure the content type is str
                )
            ],
        )

        return response
