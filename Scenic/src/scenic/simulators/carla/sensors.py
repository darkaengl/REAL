import time
from scenic import log_utils
# import logging

# log_utils.setup_logging()

import carla
import numpy as np

from scenic.core.sensors import ActiveSensor
import os
import cv2
import torch
import numpy as np
import cv2
from time import time
import pygame
import threading
from datetime import datetime



class CarlaVisionSensor(ActiveSensor):
    def __init__(
        self,
        offset=(0, 0, 0),
        rotation=(0, 0, 0),
        attributes=None,
        blueprint="sensor.camera.rgb",
        convert=None,
        record_npy=False,
    ):
        super().__init__()
        self.transform = carla.Transform(
            carla.Location(x=offset[0], y=offset[1], z=offset[2]),
            carla.Rotation(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]),
        )
        self.blueprint = blueprint
        if isinstance(attributes, str):
            raise NotImplementedError(
                "String parsing for attributes is not yet implemented. Feel free to do so."
            )
        elif isinstance(attributes, dict):
            self.attributes = attributes
        else:
            self.attributes = {}

        self.convert = None
        if convert is not None:
            if isinstance(convert, int):
                self.convert = convert
            elif isinstance(convert, str):
                self.convert = carla.ColorConverter.names[convert]
            else:
                AttributeError("'convert' has to be int or string.")

        self.record_npy = record_npy

    def save_last_observation(self, save_path, frame_number=None):
        raise NotImplementedError()


class CarlaRGBSensor(CarlaVisionSensor):
    def __init__(
        self, offset=(0, 0, 0), rotation=(0, 0, 0), attributes=None, record_npy=False
    ):
        super().__init__(
            offset=offset,
            rotation=rotation,
            attributes=attributes,
            blueprint="sensor.camera.rgb",
            convert=None,
            record_npy=record_npy,
        )

    def processing(self, data):
        array = np.frombuffer(data.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (data.height, data.width, 4))  # BGRA format
        array = array[:, :, :3]  # Take only RGB
        array = array[:, :, ::-1]  # Revert order

        return array, data.frame

    def save_last_observation(self, save_path, frame_number=None):
        # Get current time with microsecond precision
        current_time = datetime.now()

        # Format the time as a string with milliseconds
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

        if frame_number is None:
            frame_number = self.frame
        save_as = os.path.join(save_path, f"{frame_number}_{current_time}")
        if self.record_npy:
            np.save(save_as, self.observation)
        else:
            cv2.imwrite(f"{save_as}.png", self.observation[..., ::-1])
    
    ''' uncomment me and extend me for carla only implementation'''
    # def run_yolo_detection(self, *args: Any, **kwds: Any) -> Any:
    #     # resized_frame = cv2.resize(self.observation, (640, 640))
    #     results = self.model(self.observation)
    #     logging.info(self)
    #     # Get detection results as a pandas dataframe
    #     df = results.pandas().xyxy[0]
    #     # print(df)
    #     # Filter detections for class 0 ('person') with confidence over 85%
    #     person_detections = df[(df["class"] == 0) & (df["confidence"] > 0.85)]
    #     if not person_detections.empty:
    #         # print("High confidence person detections:")
    #         # for index, row in person_detections.iterrows():
    #         #     confidence = row["confidence"] * 100  # Convert to percentage
    #         # print(f"Detection {index}: {confidence:.2f}% confidence")
    #         self.pedestrian_detected = True
    #         return self.pedestrian_detected
    #     return self.pedestrian_detected


class CarlaSSSensor(CarlaVisionSensor):
    def __init__(
        self,
        offset=(0, 0, 0),
        rotation=(0, 0, 0),
        attributes=None,
        convert=None,
        record_npy=False,
    ):
        super().__init__(
            offset=offset,
            rotation=rotation,
            attributes=attributes,
            blueprint="sensor.camera.semantic_segmentation",
            convert=convert,
            record_npy=record_npy,
        )

    def processing(self, data):
        if self.convert is not None:
            data.convert(self.convert)

        array = np.frombuffer(data.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (data.height, data.width, 4))  # BGRA format

        if self.convert is not None:
            array = array[:, :, :3]  # Take only RGB
            array = array[:, :, ::-1]  # Revert order
        else:
            array = array[:, :, 2]  # Take only R

        return array, data.frame

    def save_last_observation(self, save_path, frame_number=None):
        # Get current time with microsecond precision
        current_time = datetime.now()

        # Format the time as a string with milliseconds
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

        if frame_number is None:
            frame_number = self.observation.frame
        save_as = os.path.join(save_path, f"{frame_number}_{current_time}")
        if self.record_npy:
            np.save(save_as, self.observation)
        else:
            if self.convert is not None:
                cv2.imwrite(f"{save_as}.png", self.observation[..., ::-1])
            else:
                cv2.imwrite(f"{save_as}.png", self.observation)
