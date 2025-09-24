import streamlit as st
from streamlit.components.v1 import html
# from scripts.redsl.grammar import DSL
import requests, redis
from time import time
import pandas as pd
import matplotlib.pyplot as plt
import mlflow, re, os
import hashlib
from mlflow.tracking import MlflowClient


# Set the layout to wide
st.set_page_config(layout="wide")

env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
# mlflow.set_tracking_uri(uri="http://localhost:5000")
# os.environ["MLFLOW_TRACKING_URI"] = env.get('mlflow_tracking_uri')
# st.code(mlflow.get_tracking_uri())

validate_url = "http://127.0.0.1:7999/validate"

st.title("Requirements Evolution")

on = st.toggle("visualise Test Cases")
env.set('visualize',str(on))

# print(env.get('visualize'))

# for percent_complete in range(100):
#     time.sleep(0.01)

# exp_title = st.text_input("Experiment Name", "New_Experiment")
# st.code(exp_title)

def generate_run_id(model, braking):
    param_string = f"{model}_{braking}"
    return hashlib.md5(param_string.encode()).hexdigest()

def get_metrics_by_unique_hash(experiment, unique_hash_id):
    """
    Check if a run with the given unique_hash_id exists in the specified experiment.
    If found, return the metrics of that run; otherwise, return None.

    :param experiment: MLflow experiment object.
    :param unique_hash_id: The unique identifier stored as a tag.
    :return: Dictionary of metrics if the run exists, else None.
    """
    client = MlflowClient()

    if experiment is None:
        print("Experiment not found.")
        return None

    experiment_id = experiment.experiment_id

    # Search for runs with the matching unique_hash_id tag
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.unique_hash_id = '{unique_hash_id}'",
        order_by=["start_time DESC"],  # Get the latest run first
        max_results=1
    )

    if runs:
        run = runs[0]  # Get the latest matching run
        return run.data.metrics  # Return metrics of the matching run

    return None  # No matching run found

# run_id = generate_run_id(env.get('model'), env.get('braking'))

   

if st.session_state['requirement'] != None:
    st.code(st.session_state['requirement'])
    title = env.get('model') + '_' + env.get('braking')
    exp_title = st.text_input("Experiment Name", title)
    if st.button('Evaluate Test-Cases', use_container_width=True):
        cnt = 0
        progress_text = f"Scenarios are being Evaluated. Please wait."
        my_bar = st.progress(0, text=progress_text)
        client = MlflowClient(tracking_uri="http://localhost:5000")
        for id,testcase in enumerate(st.session_state['testcases']):
            progress_text = f"Scenario-{id} is being Evaluated. Please wait."
            cnt += 1
            percent_complete = int(100*cnt/len(st.session_state['testcases']))
            
            experiment = client.get_experiment_by_name(exp_title)

            if experiment is None:
                experiment_id = client.create_experiment(exp_title)
            elif experiment and experiment.lifecycle_stage == "deleted":
                client.delete_experiment(experiment.experiment_id)  # Permanently deletes it
                experiment_id = client.create_experiment(exp_title)
            else:
                experiment_id = experiment.experiment_id

            # Start a new run
            run = client.create_run(experiment_id)

            # mlflow.set_experiment(exp_title)  # Must be set before `start_run()`

            # with mlflow.start_run(experiment_id=experiment_id):
            # Set tags
            client.set_tag(run.info.run_id, "model", env.get('model'))
            client.set_tag(run.info.run_id, "braking", env.get('braking'))

            def replace_with_value(match):
                return match.group(2)

            matches = re.findall(r'({.*?})', testcase)
            matches = [item.strip('{}').strip(' ').split(':') for item in matches]
            param_dict = {key.strip(' '): value.strip(' ') for key, value in matches}
            # Substitute each {key : value} with just the value
            rule = re.sub(r'\{\s*(\w+)\s*:\s*([\w\.\d]+)\s*\}', replace_with_value, testcase)

            params_ = {'goal': testcase, 'params': param_dict, 'rule': rule}
            unique_hash_id = hashlib.md5(str(sorted(params_.items())).encode()).hexdigest()

            # params_exist = get_metrics_by_unique_hash(experiment, unique_hash_id)
            # if params_exist:
            #     response = params_exist
            #     st.code(str(response))
            # else:
            try:                    
                response = requests.get(validate_url, params={'testcase':testcase}).json()
                # st.code(response)
            except:
                if st.button('Validate', use_container_width=False, key=id):
                    response = requests.get(validate_url, params={'testcase':testcase}).json()

            if response['STATUS']!='NOT EXECUTED':
                for key, value in params_.items():
                    client.log_param(run.info.run_id, key, value)
                client.set_tag(run.info.run_id, "unique_run_hash", unique_hash_id)
                # client.log_params(run.info.run_id, params_)
                client.log_metric(run.info.run_id, "Total Test Cases", response['total'])
                client.log_metric(run.info.run_id, "Passed Test Cases", response['passed'])
                client.log_metric(run.info.run_id, "Failed Test Cases", response['failed'])
                client.log_metric(run.info.run_id, "Percentage of testcase passed", 100 * response['passed'] / response['total'])

        
                # st.code(str(percent_complete)+'::'+str(cnt/len(st.session_state['testcases'])))
                left_, right_= st.tabs(['testcase','results'])
                with st.expander(f'Scenario {id}', expanded=True):
                    with left_:
                        st.code(testcase,wrap_lines=True)
                        # st.code(response)
                    with right_:
                        # response['color'] = ['green', 'red', 'blue']
                        # Creating DataFrame
                        # data = pd.DataFrame({'Category': ['Passed', 'Failed'], 'Passed': response['passed'], 'Failed' : response['failed']})

                        # # Setting the index to 'Category' so Streamlit correctly renders the bar chart
                        # data.set_index('Category', inplace=True)

                        # # Display bar chart
                        # st.bar_chart(data, color=['#28a745', '#dc3545'])  # Use a hex color code for clarity
                        

                        labels = 'Passed', 'Failed'
                        sizes = [response['passed'], response['failed']]
                        explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

                        fig1, ax1 = plt.subplots(figsize=(1,1))
                        ax1.pie(sizes, explode=explode, labels=labels, # autopct='%1.1f%%',
                                shadow=True, startangle=90)
                        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                        st.pyplot(fig1, use_container_width=False)

            my_bar.progress(percent_complete, text=progress_text)
        my_bar.empty()
        mlflow.end_run()

else:
    st.code('No grammar is selected !!!')

