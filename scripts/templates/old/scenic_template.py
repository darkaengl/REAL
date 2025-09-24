import numpy as np

def get_pedestrian(pedestrian,dress):

    if pedestrian=='Adult' and dress=='Light':
        return "walker.pedestrian.0008"
    elif pedestrian=='Adult' and dress=='Dark':
        return "walker.pedestrian.0007"
    elif pedestrian=='Child' and dress=='Light':
        return "walker.pedestrian.0048"
    elif pedestrian=='Child' and dress=="Dark":
        return "walker.pedestrian.0013"
    
def get_ego_behavior(mitigation):

    if mitigation!='proportional_braking':
        ego_behaviour = """
behavior Exp_EgoBehaviour():
    try:
        do FollowLaneBehavior(target_speed = EGO_SPEED)
    interrupt when checkPedestrianDectectedFlag(ego.observations["front_rgb"], pedestrian.position, ego.position):
        print('yolo emergency braking')
        take YoloEmergencyBraking()
"""
    else:
        ego_behaviour = """
behavior Exp_EgoBehaviour():
    try:
        do FollowLaneBehavior(target_speed=10)
    interrupt when checkCautionBehaviour(ego.observations["front_rgb"], pedestrian.position, ego.position):
        adjusted_brake_value = checkCautionBehaviour(ego.observations["front_rgb"], pedestrian.position, ego.position)
        print(f'target braking: {adjusted_brake_value}')
        take SetBrakeAction(adjusted_brake_value)
    interrupt when checkPedestrianDectectedFlag(ego.observations["front_rgb"], pedestrian.position, ego.position):
        print('yolo emergency braking')
        take YoloEmergencyBraking()
"""

    return ego_behaviour

def get_pedestrian_pos(direction, distance):

    # print(f'direction :: {direction} | distance :: {distance}')
    # return '(-3, 12, 0)'

    if direction=='LR' and distance=='Long':
        return '(-3, 12, 0)'
    elif direction=='RL' and distance=='Long':
        return '(3, 12, 0)'
    elif direction=='RL' and distance=='Short':
        return '(3, 7, 0)'
    elif direction=='LR' and distance=='Short':
        return '(-1, 7, 0)'
    
def get_pedestrian_angle(direction, distance):

    if direction=='LR' and distance=='Long':
        return '90'
    elif direction=='RL' and distance=='Long':
        return '180'
    elif direction=='RL' and distance=='Short':
        return '180'
    elif direction=='LR' and distance=='Short':
        return '90'
    # return '90'

def get_lane():

    lane = np.random.choice([2,9,11,13,20,25])

    return lane
    



def get_scenic_code(params):

    code = f"""
# SET SCENARIO PARAMETERS AND MODEL 
import carla
import numpy as np
import logging
import time
import os
import sys
#from scenic.log_utils import setup_logging
import random

# Define the weather conditions
weather = {{
    "cloudiness":50,
    "precipitation":0,
    "sun_azimuth_angle":120,
    "sun_altitude_angle":60,
    "fog_density": {params['fog_density']}
}}

# Apply the weather conditions to the scenario
param map = localPath('/opt/carla/CarlaUE4/Content/Carla/Maps/OpenDrive/Town01.xodr')
param carla_map = 'Town01'

model scenic.simulators.carla.model  # Here the definitions of all referenceables are defined (vehicle types, road library, etc) 
param weather = weather
# SCENARIO CONSTANTS 
EGO_MODEL = "vehicle.tesla.model3"
PEDESTRIAN_MODEL = '{get_pedestrian(params['pedestrian'], params['dress'])}'
EGO_SPEED = 8
SAFETY_DISTANCE = 10
BRAKE_INTENSITY = 1.0
PEDESTRIAN_MIN_SPEED = 1.0
THRESHOLD = 8

# SENSOR ATTRIBUTES
attrs = {{"image_size_x": 640,
        "image_size_y": 640}}

## DEFINING SPATIAL RELATIONS

all_lanes = network.lanes  # Get all lanes in the network
chosen_lane = Uniform(*[all_lanes[2], all_lanes[9], all_lanes[11], all_lanes[13], all_lanes[25]])  # Randomly pick an index
lane = chosen_lane # all_lanes[chosen_index]  # Select the lane # 2,9,11,13,20,25 (16, 17)
spot = new OrientedPoint on lane.centerline
vending_spot = new OrientedPoint following roadDirection from spot for -3



{get_ego_behavior(params['braking'])}

behavior PedestrianBehavior(min_speed=PEDESTRIAN_MIN_SPEED, threshold=8):
    do CrossingBehavior(ego, min_speed, threshold)

pedestrian = new Pedestrian at {get_pedestrian_pos(params['direction'], params['distance'])} relative to spot,  
    with heading {get_pedestrian_angle(params['direction'], params['distance'])} deg relative to roadDirection,  
    with regionContainedIn None,
    with behavior PedestrianBehavior(PEDESTRIAN_MIN_SPEED, THRESHOLD),
    with blueprint PEDESTRIAN_MODEL

vending_machine = new VendingMachine right of vending_spot by 3,
    with heading 90 deg relative to vending_spot.heading,
    with regionContainedIn None  # Allow the actor to spawn outside the driving lanes

ego = new Car following roadDirection from spot for -15,
    with blueprint EGO_MODEL,
    with sensors {{"front_rgb": RGBSensor(offset=(1.6, 0, 1.7), attributes=attrs)}}, #(201 -> low) (x-> horizontal front back, y -> horizontal left right, z -> vertical up down)
    with behavior Exp_EgoBehaviour()

# RECORDING SETUP
record ego.observations["front_rgb"] as "front_rgb"
# require monitor RecordingMonitor(ego, path=localPath(f"/home/recording/temp"), recording_start=5, subsample=2)
record roadDirection at spot as "road_direction"

# REQUIREMENTS
require (distance to intersection) > 30
require (distance from spot to intersection) > 30
require always (ego.laneSection._slowerLane is None)
require always (ego.laneSection._fasterLane is None)

# TERMINATION CONDITION
terminate when (distance to spot) > 30
    """
    
    return code
