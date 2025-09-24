from typing import Union
import re
from fastapi import FastAPI
from scripts.redsl.grammar import DSL
from scripts.evolve.ge import start_ge
import uvicorn

from scripts.evolve.util import falsifier
from scripts.templates.old.scenic_template import get_scenic_code
import redis, re

import multiprocessing as mp


env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/verify_requirement")
def verify_requirement(requirement: str = None):

    dsl = DSL(requirement)

    try: 
        return {"parsed_grammar" : dsl.parse_tree.pretty(), "STATUS":"OK"}
    except Exception as e:
        return {"error" : str(e), "STATUS" : "NOT OK"}
    
@app.get("/get_testcases")
def get_testcases(requirement: str = None):

    dsl = DSL(requirement)
    scenario = dsl.get_scenario()
    testcases = start_ge(sample=True)
    

    try: 
        return {"testcases" : testcases, "STATUS" : "OK"}
    except Exception as e:
        return {"error" : str(e), "STATUS" : "NOT OK"}


@app.get("/get_testcases")
def get_testcases(requirement: str = None):

    dsl = DSL(requirement)
    scenario = dsl.get_scenario()
    testcases = start_ge(sample=True)
    

    try: 
        return {"testcases" : testcases, "STATUS" : "OK"}
    except Exception as e:
        return {"error" : str(e), "STATUS" : "NOT OK"}
    
def _validate(q, testcase, braking):

        def replace_with_value(match):
                return match.group(2)

        text = testcase
        print(text)
        matches = re.findall(r'({.*?})', text)
        matches = [item.strip('{}').strip(' ').split(':') for item in matches]
        param_dict = {key.strip(' '): value.strip(' ') for key, value in matches}
        param_dict['braking'] = braking

        # Substitute each {key : value} with just the value
        rule = re.sub(r'\{\s*(\w+)\s*:\s*([\w\.\d]+)\s*\}', replace_with_value, text)

        print(rule)

        code = get_scenic_code(params=param_dict)

        # print(param_dict)

        f = falsifier(code, 2000)
        fitness = f.falsify(num_test=10)

        q.put(fitness)
    
@app.get("/validate")
def validate(testcase: str = None):

    retries = 0
    while retries < 10:

        q = mp.Queue()
        process = mp.Process(target=_validate, args=(q,testcase, env.get('braking'),))
        process.start()
        process.join(timeout=100)  # Wait for the process to finish

        if process.is_alive():
            print("CARLA task exceeded time limit. Terminating...")
            process.terminate()
            process.join()
            validate(testcase=testcase)
            retries += 1
        else:
            if not q.empty():
                response = q.get()
                response['STATUS'] = 'OK'
                return   response
            else:
                break
    return {'STATUS':'NOT EXECUTED'}
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7999)