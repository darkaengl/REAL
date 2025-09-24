"""Behaviors for dynamic agents in CARLA scenarios."""
from scenic.domains.driving.behaviors import *	# use common driving behaviors

try:
    from scenic.simulators.carla.actions import *
except ModuleNotFoundError:
    pass    # ignore; error will be caught later if user attempts to run a simulation

behavior AutopilotBehavior():
    """Behavior causing a vehicle to use CARLA's built-in autopilot."""
    take SetAutopilotAction(True)

behavior WalkForwardBehavior(speed=0.5):
    take SetWalkingDirectionAction(self.heading), SetWalkingSpeedAction(speed)

behavior WalkBehavior(maxSpeed=1.4):
    take SetWalkAction(True, maxSpeed)

behavior CrossingBehavior(reference_actor, min_speed=1, threshold=10, final_speed=None):
    """
    This behavior dynamically controls the speed of an actor that will perpendicularly (or close to)
    cross the road, so that it arrives at a spot in the road at the same time as a reference actor.

    Args:
        min_speed (float): minimum speed of the crossing actor. As this is a type of "synchronization action",
            a minimum speed is needed, to allow the actor to keep moving even if the reference actor has stopped
        threshold (float): starting distance at which the crossing actor starts moving
        final_speed (float): speed of the crossing actor after the reference one surpasses it
    """

    if not final_speed:
        final_speed = min_speed

    while (distance from self to reference_actor) > threshold:
        wait

    while True:
        distance_vec = self.position - reference_actor.position
        rotated_vec = distance_vec.rotatedBy(-reference_actor.heading)

        ref_dist = rotated_vec.y
        if ref_dist < 0:
            # The reference_actor has passed the crossing object, no need to keep monitoring the speed
            break

        actor_dist = rotated_vec.x

        ref_speed = reference_actor.speed
        ref_time = ref_speed / ref_dist

        actor_speed = actor_dist * ref_time
        if actor_speed < min_speed:
            actor_speed = min_speed

        if isinstance(self, Walks):
            do WalkForwardBehavior(actor_speed)
        elif isinstance(self, Steers):
            take SetSpeedAction(actor_speed)

    if isinstance(self, Walks):
        do WalkForwardBehavior(final_speed)
    elif isinstance(self, Steers):
        take SetSpeedAction(final_speed)

# behavior Exp_FollowLaneBehavior(target_speed = 10, laneToFollow=None, is_oppositeTraffic=False):
#     ''' 
#     Follow's the lane on which the vehicle is at, unless the laneToFollow is specified.
#     Once the vehicle reaches an intersection, by default, the vehicle will take the straight route.
#     If straight route is not available, then any availble turn route will be taken, uniformly randomly. 
#     If turning at the intersection, the vehicle will slow down to make the turn, safely. 

#     This behavior does not terminate. A recommended use of the behavior is to accompany it with condition,
#     e.g. do FollowLaneBehavior() until ...

#     :param target_speed: Its unit is in m/s. By default, it is set to 10 m/s
#     :param laneToFollow: If the lane to follow is different from the lane that the vehicle is on, this parameter can be used to specify that lane. By default, this variable will be set to None, which means that the vehicle will follow the lane that it is currently on.
#     '''

#     past_steer_angle = 0
#     past_speed = 0 # making an assumption here that the agent starts from zero speed
#     if laneToFollow is None:
#         current_lane = self.lane
#     else:
#         current_lane = laneToFollow

#     current_centerline = current_lane.centerline
#     in_turning_lane = False # assumption that the agent is not instantiated within a connecting lane
#     intersection_passed = False
#     entering_intersection = False # assumption that the agent is not instantiated within an intersection
#     end_lane = None
#     original_target_speed = target_speed
#     TARGET_SPEED_FOR_TURNING = 5 # KM/H
#     TRIGGER_DISTANCE_TO_SLOWDOWN = 10 # FOR TURNING AT INTERSECTIONS

#     if current_lane.maneuvers != ():
#         nearby_intersection = current_lane.maneuvers[0].intersection
#         if nearby_intersection == None:
#             nearby_intersection = current_lane.centerline[-1]
#     else:
#         nearby_intersection = current_lane.centerline[-1]
    
#     # instantiate longitudinal and lateral controllers
#     _lon_controller, _lat_controller = simulation().getLaneFollowingControllers(self)

#     while True:

#         if self.speed is not None:
#             current_speed = self.speed
#         else:
#             current_speed = past_speed

#         if not entering_intersection and (distance from self.position to nearby_intersection) < TRIGGER_DISTANCE_TO_SLOWDOWN:
#             entering_intersection = True
#             intersection_passed = False
#             straight_manuevers = filter(lambda i: i.type == ManeuverType.STRAIGHT, current_lane.maneuvers)

#             if len(straight_manuevers) > 0:
#                 select_maneuver = Uniform(*straight_manuevers)
#             else:
#                 if len(current_lane.maneuvers) > 0:
#                     select_maneuver = Uniform(*current_lane.maneuvers)
#                 else:
#                     take SetBrakeAction(1.0)
#                     break

#             # assumption: there always will be a maneuver
#             if select_maneuver.connectingLane != None:
#                 current_centerline = concatenateCenterlines([current_centerline, select_maneuver.connectingLane.centerline, \
#                     select_maneuver.endLane.centerline])
#             else:
#                 current_centerline = concatenateCenterlines([current_centerline, select_maneuver.endLane.centerline])

#             current_lane = select_maneuver.endLane
#             end_lane = current_lane

#             if current_lane.maneuvers != ():
#                 nearby_intersection = current_lane.maneuvers[0].intersection
#                 if nearby_intersection == None:
#                     nearby_intersection = current_lane.centerline[-1]
#             else:
#                 nearby_intersection = current_lane.centerline[-1]

#             if select_maneuver.type != ManeuverType.STRAIGHT:
#                 in_turning_lane = True
#                 target_speed = TARGET_SPEED_FOR_TURNING

#                 do TurnBehavior(trajectory = current_centerline)


#         if (end_lane is not None) and (self.position in end_lane) and not intersection_passed:
#             intersection_passed = True
#             in_turning_lane = False
#             entering_intersection = False 
#             target_speed = original_target_speed
#             _lon_controller, _lat_controller = simulation().getLaneFollowingControllers(self)

#         nearest_line_points = current_centerline.nearestSegmentTo(self.position)
#         nearest_line_segment = PolylineRegion(nearest_line_points)
#         cte = nearest_line_segment.signedDistanceTo(self.position)
#         if is_oppositeTraffic:
#             cte = -cte

#         speed_error = target_speed - current_speed

#         # compute throttle : Longitudinal Control
#         throttle = _lon_controller.run_step(speed_error)

#         # compute steering : Lateral Control
#         current_steer_angle = _lat_controller.run_step(cte)
#         z = PedestrianDetectionStatus.get_pedestrian_detected()
#         logging.info(z)
#         if simulation().pedestrian_detected == True:
#             take YoloEmergencyBraking()
#             simulation().pedestrian_detected = False
#             take RegulatedControlAction(throttle, current_steer_angle, past_steer_angle)
#             past_steer_angle = current_steer_angle
#             past_speed = current_speed
#         else:
#             take RegulatedControlAction(throttle, current_steer_angle, past_steer_angle)
#             past_steer_angle = current_steer_angle
#             past_speed = current_speed