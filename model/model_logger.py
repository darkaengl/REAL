import os
import mlflow
import torch 
import redis

from torch import nn
from torch.utils.data import DataLoader
# from torchinfo import summary
# from torchmetrics import Accuracy
from torchvision import datasets
from torchvision.transforms import ToTensor


# Connect to Redis
env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
env.set("mlflow_tracking_uri", "http://127.0.0.1:5000")
env.set("experiment_log_yolo", "yolo models")


mlflow.set_tracking_uri(uri=env.get('mlflow_tracking_uri'))
mlflow.set_experiment(env.get("experiment_log_yolo"))

MODELS = {
    "few_shot" : torch.hub.load("ultralytics/yolov5", "custom", path="./few_shot.pt", force_reload=True),
    "fine_tune" : torch.hub.load("ultralytics/yolov5", "custom", path="./fine_tune.pt", force_reload=True),
    "yolov5m" : torch.hub.load("ultralytics/yolov5", "custom", path="./yolov5m.pt", force_reload=True),
    "yolov5s" : torch.hub.load("ultralytics/yolov5", "custom", path="./yolov5s.pt", force_reload=True)
}


for key,model in MODELS.items():

    scripted_model = torch.jit.script(model)

    model_info = mlflow.pytorch.log_model(scripted_model, key)
    env.set(f"{key}_model_uri", model_info.model_uri)