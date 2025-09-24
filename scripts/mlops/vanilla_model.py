import mlflow
from mlflow.models import infer_signature

import ultralytics
import time
import cv2
import torch
import numpy as np
import os

# model_name = os.environ.get('YOLO_MODEL', 'yolov5m')

# # Update the model loading code
# current_dir = os.getcwd()
# model_path = os.path.join(current_dir, "model", f"{model_name}.pt")
# # model_path = os.path.join(current_dir, "model", "best.pt")

# yolo_model = torch.hub.load("ultralytics/yolov5", "custom", path=model_path, force_reload=True)

from ultralytics import YOLO

os.environ["MLFLOW_TRACKING_URI"] = "http://127.0.0.1:5000"

# # Set our tracking server uri for logging
mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")

# # Create a new MLflow Experiment
mlflow.set_experiment("YOLO Models")

# Create a new YOLO model from scratch
# model = YOLO("yolo11n.yaml")

model_name = 'yolov5s'

# Load a pretrained YOLO model (recommended for training)
# model = YOLO("yolo11n.pt")
model = torch.hub.load(f'ultralytics/yolov5', model_name, pretrained=True)

print(model)

# # Start an MLflow run
# with mlflow.start_run():
#     # Train the model using the 'coco8.yaml' dataset for 3 epochs
#     results = model.train(data="coco8.yaml", epochs=3)
#     # Log the hyperparameters
#     # mlflow.log_params({'name':'YOLOV5m'})

#     # Evaluate the model's performance on the validation set
#     results = model.val()

#     onnx_model = model.export(format="onnx")

#     train,test = 



#     model_signature = infer_signature(train_x, train_y)

#     mlflow.sklearn.log_model(onnx_model, model_name, signature=model_signature, registered_model_name="sk-learn-elasticnet-model",)


# print('Results : ', results)

# Perform object detection on an image using the model
# results = model("https://ultralytics.com/images/bus.jpg")

# Export the model to ONNX format
# 








#     # Log the loss metric
#     # mlflow.log_metric("accuracy", accuracy)

#     # Set a tag that we can use to remind ourselves what this run was for
#     mlflow.set_tag("Training Info", "Publicly available models without further training")

#     # Infer the model signature
#     signature = infer_signature(X_train, lr.predict(X_train))

#     # Log the model
#     # model_info = mlflow.sklearn.log_model(
#     #     sk_model=lr,
#     #     artifact_path="iris_model",
#     #     signature=signature,
#     #     input_example=X_train,
#     #     registered_model_name="tracking-quickstart",
#     # )

#     model_info = mlflow.pytorch.log_model(yolo_model,'YOLOV5m')
#     mlflow.pytorch.log_model(yolo_model, 'YOLOV5m', signature=model_signature, registered_model_name="sk-learn-elasticnet-model",)
