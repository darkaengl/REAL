# from scripts.rl_env.scenic_env import ScenicEnv
from scripts.evolve.util import falsifier, get_scenic_script
from scripts.templates.old.scenic_template import get_scenic_code
import redis, re

env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
env.set('model', 'yolov5s')
env.set('braking', 'proportional_braking')


# Create Scenic-based environment
# env = ScenicEnv('/home/darkaengl/Project/REAL/scripts/scenarios/scratch.scenic')

import scenic
from scenic.simulators.carla.simulator import CarlaSimulator



# scenario = scenic.scenarioFromFile('/home/darkaengl/Project/REAL/scripts/scenarios/scratch.scenic',
#                                    model='scenic.simulators.carla.model',
#                                    mode2D=True)
# scene, _ = scenario.generate()
# simulator = CarlaSimulator('Town01', '/opt/carla/CarlaUE4/Content/Carla/Maps/OpenDrive/Town01.xodr',timestep=0.01, render=False, port=2010)
# simulation = simulator.simulate(scene, maxSteps=50)
# if simulation: 
#         result = simulation.result
#         for i, state in enumerate(result.trajectory):
#                 print(state)


# self.sampler.scenario.getSimulator()

# with open('/home/darkaengl/Project/REAL/scripts/scenarios/scratch.scenic','r') as f:
#     code = f.read()

code = """
# SET SCENARIO PARAMETERS AND MODEL 
import carla
import logging
import time
import os
import sys
#from scenic.log_utils import setup_logging
import random

# Define the weather conditions
weather = {
    "cloudiness":50,
    "precipitation":0,
    "sun_azimuth_angle":120,
    "sun_altitude_angle":60,
    "fog_density": 50
}

# Apply the weather conditions to the scenario
param map = localPath('/opt/carla/CarlaUE4/Content/Carla/Maps/OpenDrive/Town01.xodr')
param carla_map = 'Town01'

model scenic.simulators.carla.model  # Here the definitions of all referenceables are defined (vehicle types, road library, etc) 
param weather = weather
# SCENARIO CONSTANTS 
EGO_MODEL = "vehicle.tesla.model3"
PEDESTRIAN_MODEL = "walker.pedestrian.0007"
EGO_SPEED = 8
SAFETY_DISTANCE = 10
BRAKE_INTENSITY = 1.0
PEDESTRIAN_MIN_SPEED = 1.0
THRESHOLD = 8

# SENSOR ATTRIBUTES
attrs = {"image_size_x": 640,
        "image_size_y": 640}

## DEFINING SPATIAL RELATIONS
lane = Uniform(*network.lanes)
spot = new OrientedPoint on lane.centerline
vending_spot = new OrientedPoint following roadDirection from spot for -3


behavior Exp_EgoBehaviour():
    try:
        do FollowLaneBehavior(target_speed = EGO_SPEED)
    interrupt when checkPedestrianDectectedFlag(ego.observations["front_rgb"], pedestrian.position, ego.position):
        print('yolo emergency braking')
        take YoloEmergencyBraking()


behavior PedestrianBehavior(min_speed=PEDESTRIAN_MIN_SPEED, threshold=8):
    do CrossingBehavior(ego, min_speed, threshold)

pedestrian = new Pedestrian at (-3, 12, 0) relative to spot,  
    with heading 90 deg relative to roadDirection,  
    with regionContainedIn None,
    with behavior PedestrianBehavior(PEDESTRIAN_MIN_SPEED, THRESHOLD),
    with blueprint PEDESTRIAN_MODEL

vending_machine = new VendingMachine right of vending_spot by 3,
    with heading 90 deg relative to vending_spot.heading,
    with regionContainedIn None  # Allow the actor to spawn outside the driving lanes

ego = new Car following roadDirection from spot for -15,
    with blueprint EGO_MODEL,
    with sensors {"front_rgb": RGBSensor(offset=(1.6, 0, 1.7), attributes=attrs)}, #(201 -> low) (x-> horizontal front back, y -> horizontal left right, z -> vertical up down)
    with behavior Exp_EgoBehaviour()

# RECORDING SETUP
record ego.observations["front_rgb"] as "front_rgb"
# require monitor RecordingMonitor(ego, path=localPath(f"/home/recording/temp"), recording_start=5, subsample=2)

# REQUIREMENTS
require (distance to intersection) > 30
require (distance from spot to intersection) > 30
require always (ego.laneSection._slowerLane is None)
require always (ego.laneSection._fasterLane is None)

# TERMINATION CONDITION
terminate when (distance to spot) > 30
"""

testcase = """A { pedestrian : Adult } wearing a {dress : Dark} dress trying to cross road from { direction : LR } at { distance : Short } distance on a day with fog density {fog_density : 0}"""

def replace_with_value(match):
            return match.group(2)

text = testcase
matches = re.findall(r'({.*?})', text)
matches = [item.strip('{}').strip(' ').split(':') for item in matches]
param_dict = {key.strip(' '): value.strip(' ') for key, value in matches}
param_dict['braking'] = env.get('braking')
# Substitute each {key : value} with just the value
rule = re.sub(r'\{\s*(\w+)\s*:\s*([\w\.\d]+)\s*\}', replace_with_value, text)

code = get_scenic_code(params=param_dict)

# code = get_scenic_script(param_dict, './scripts/scenarios/scratch.temp')

# print(code)

f = falsifier(code, 2000)
fitness = f.falsify(num_test=2)

print(fitness)


# sim = falsifier(code, 2000)
# result = sim.falsify()

# print(result)