import scenic
from scenic.simulators.carla import CarlaSimulator
import warnings

warnings.filterwarnings('ignore')

def evaluate(code : str = None):
    if code:
        scenario = scenic.scenarioFromString(code,
                                            model='scenic.simulators.carla.model',
                                            mode2D=True)
    else:
        scenario = scenic.scenarioFromFile('/home/darkaengl/Project/REAL/scripts/scenarios/sc-1.scenic',
                                        model='scenic.simulators.carla.model',
                                        mode2D=True)
    carla_map_path = '/opt/carla/CarlaUE4/Content/Carla/Maps/OpenDrive/Town01.xodr'
    carla_map = 'Town01'
    scene, _ = scenario.generate()
    simulator = CarlaSimulator(carla_map=carla_map, map_path=carla_map_path, render=True)
    simulation = simulator.simulate(scene, maxSteps=1000)
    DIST = []
    if simulation:  # `simulate` can return None if simulation fails
            result = simulation.result
            objects = simulation.objects
            for i, state in enumerate(result.trajectory):
                carPos, pedestrianPos, vendingPos = state
                dist = carPos.distanceTo(pedestrianPos)
                DIST.append(dist)
                if dist < 2:
                    print(f'{i} Unsafe')
                else:
                    print(f'{i} safe')
    return DIST

if __name__=='__main__':
    import time

    start_time = time.time()
    evaluate()
    print("--- %s seconds ---" % (time.time() - start_time))
     
     