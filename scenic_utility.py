from scripts.evolve.util import falsifier
from scripts.templates.old.scenic_template import get_scenic_code
import redis, re

def validate(testcase: str = None):

    env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    def replace_with_value(match):
            return match.group(2)

    text = testcase
    print(text)
    matches = re.findall(r'({.*?})', text)
    matches = [item.strip('{}').strip(' ').split(':') for item in matches]
    param_dict = {key.strip(' '): value.strip(' ') for key, value in matches}
    param_dict['braking'] = env.get('braking')

    # Substitute each {key : value} with just the value
    rule = re.sub(r'\{\s*(\w+)\s*:\s*([\w\.\d]+)\s*\}', replace_with_value, text)

    code = get_scenic_code(params=param_dict)

    # print(param_dict)

    f = falsifier(code, 2000)
    fitness = f.falsify(num_test=2)

    return fitness