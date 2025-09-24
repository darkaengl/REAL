import re
import math
import os.path
import sys
import random, scenic

from dotmap import DotMap

from verifai.samplers import ScenicSampler
from verifai.scenic_server import ScenicServer
from verifai.falsifier import generic_falsifier, generic_parallel_falsifier
from verifai.monitor import specification_monitor, mtl_specification

import os 
import mlflow
from tqdm import tqdm
import redis

# Connect to Redis
env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# os.environ["MLFLOW_TRACKING_URI"] = env.get('mlflow_tracking_uri')


def get_scenic_script(param_dict, template):

    with open(template, 'r') as f:
        temp = f.read()

    # matches = re.findall(r'<(.*?)>', temp)

    for key,value in param_dict.items():
        print(key,value)
        temp = re.sub(f'<{key}>', value, temp)

    return temp


class MyMonitor(specification_monitor):
    def __init__(self):
        self.specification = mtl_specification(['G safe'])
        super().__init__(self.specification)

    def evaluate(self, simulation):

        if simulation:

            # print('simulation is successful !!!')

            # for obj in simulation.objects:
            #     print(dir(obj))

            # Get trajectories of objects from the result of the simulation
            traj = simulation.result.trajectory

            # print(simulation.result.trajectory)

            # Compute time-stamped sequence of values for 'safe' atomic proposition;
            # we'll define safe = "distance from ego to all other objects > 5"
            safe_values = []
            for positions in traj:
                ego = positions[0]
                dist = min((ego.distanceTo(other) for other in positions[1:]),
                        default=math.inf)
                safe_values.append(dist - 2)
            eval_dictionary = {'safe' : list(enumerate(safe_values)) }

            return self.specification.evaluate(eval_dictionary)

        else:
            return None
        
    
class falsifier:

    def __init__(self, code, port):
        
        if env.get('visualize')=='True':
            visualize = True
        else:
            visualize = False

        params = {'render' : visualize, 'port' : port}
        sampler = ScenicSampler.fromScenicCode(code, mode2D=True, params=params)

        # Set up the falsifier
        self.falsifier_params = DotMap(
                                        n_iters=5,
                                        verbosity=0,
                                        save_error_table=True,
                                        save_safe_table=True,
                                        # uncomment to save these tables to files; we'll print them out below
                                        # error_table_path='error_table.csv',
                                        # safe_table_path='safe_table.csv'
                                    )
        self.server_options = DotMap(maxSteps=200, verbosity=0)
        # self.server_options = dict(maxSteps=100, verbosity=0, num_workers=5)

        self.falsifier = generic_falsifier(sampler=sampler,
                                            monitor=MyMonitor(),
                                            falsifier_params=self.falsifier_params,
                                            server_class=ScenicServer,
                                            server_options=self.server_options)
        
    def falsify(self, num_test=10):

        t = 0
        p = 0
        n = 0
        with tqdm(total=num_test) as pbar:
            while t<num_test:
                sample, rho, timings = self.falsifier.server.run_server()
                if rho:
                    t += 1
                    pbar.update(1)
                    if rho > 0:
                        p += 1
                    else:
                        n+=1

        fitness = {'total' : t,
                   'passed' : p, 
                   'failed' : n}

        return fitness
    



def evaluate(ind, dummy):

    # mlflow.end_run()

    # # Create a new MLflow Experiment

    with mlflow.start_run():

        mlflow.set_experiment(f"{env.get('mlflow_experiment_name')}_testcases")
        mlflow.set_tag(env.get('mlflow_experiment_tag'), "mlflow_experiment_description")

        def replace_with_value(match):
            return match.group(2)

        text = ind.phenotype
        matches = re.findall(r'({.*?})', text)
        matches = [item.strip('{}').strip(' ').split(':') for item in matches]
        param_dict = {key.strip(' '): value.strip(' ') for key, value in matches}
        # Substitute each {key : value} with just the value
        rule = re.sub(r'\{\s*(\w+)\s*:\s*([\w\.\d]+)\s*\}', replace_with_value, text)

        code = get_scenic_script(param_dict, 'scripts/scenarios/scratch.temp')

        f = falsifier(code)
        fitness = f.falsify(num_test=2)

        mlflow.log_params({'goal': rule, 'code': code})
        mlflow.log_params(param_dict)
        mlflow.log_metric("Total Test Cases", fitness['total'])
        mlflow.log_metric("Passed Test Cases", fitness['passed'])
        mlflow.log_metric("Failed Test Cases", fitness['failed'])
        mlflow.log_metric("Percentage of testcase passed", fitness['pct'])

    return fitness,


