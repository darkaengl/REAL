import streamlit as st
from streamlit.components.v1 import html
from scripts.redsl.grammar import DSL
import requests, redis
from scenic_utility import validate

env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Set the layout to wide
st.set_page_config(layout="wide")

# Define the URL of the endpoint
verify_url = "http://127.0.0.1:7999/verify_requirement"
testcases_url = "http://127.0.0.1:7999/get_testcases"
validate_url = "http://127.0.0.1:7999/validate"

st.markdown(
    """
    <style>
    .stCodeBlock {
        font-size: 32px; /* Adjust the font size as needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)

def nav_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)

# Function to add custom button styles
def set_button_height(button_key, height):
    st.markdown(f"""
        <style>
            div[data-testid="stButton"] button[data-baseweb="button"][key="{button_key}"] {{
                height: {height}rem; /* Dynamic button height */
                font-size: 14px; /* Optional: Adjust font size */
            }}
        </style>
    """, unsafe_allow_html=True)

st.title("REAL Framework")

on = st.toggle("visualise Test Cases")
env.set('visualize',str(on))
# st.header("Add a new Requirement")

# if 'dsl' not in st.session_state:
#     st.session_state['dsl'] = DSL()
    
with st.expander("Try Out A Simple Example", expanded=True):
    st.header("A simple requirement using Limited Grammar")
    model = st.selectbox("Choose the Perception Module", ["yolov5m", "yolov5s", "fine_tune", "few_shot"])
    braking = st.selectbox("Choose braking module", ["sudden_braking", "proportional_braking"])
    env.set('model', model)
    env.set('braking', braking)
    req = f"""
            MAINTAIN "Pedestrian Safety" 
                by 
                    "Pedestrian Check" using "Perception Module"
                        operationalized as
                            "Detect Pedestrian" performed by "{model}" 
                            taking input "image" producing output "pedestrian detection confidence" & "pedestrian detection flag"
                followed by 
                    "braking" using "braking module"
                        operationalized as 
                            "Bring down throttle" & "Apply Brakes" if "pedestrian detection flag=True" performed by "{braking}" 
                            taking input "pedestrian detection flag" producing output "Braking Status Flag" 
                in scenario where
                    "A pedestrian trying to cross the street."
            """
    tab1, tab2= st.tabs(["Requirement", "Control Variables"])
    with tab1:
        st.code(req)
    with tab2:
        st.code("""
        <direction>     ::= LR | RL         # Left to right / Right to Left direction
        <distance>      ::= Short | Long    # short means 7m / Long means 12m in fron of the car
        <fog_density>   ::= 0 | 50          # Either No fog or 50% fog
        <pedestrian>    ::= Adult | Child   # Either an Adult or A child
        <dress>         ::= Light | Dark    # Light Dress / Dark Dress
        """)


left, middle, right = st.columns(3)

if left.button('Verify', use_container_width=True):
    # print(req)
    # dsl = DSL(req)
    # st.code(dsl.parse_tree.pretty())
    response = requests.get(verify_url, params={'requirement':req})
    response = response.json()
    st.write(response)

    # if response['STATUS'] == 'OK':
    #     st.write(response)

if middle.button('Generate Sample TestCases', use_container_width=True):
    response = requests.get(testcases_url, params={'requirement':req, 'sample':True}).json()
    if response['STATUS'] == 'OK':
        st.session_state['testcases'] = list(set(response['testcases']))


if 'testcases' in st.session_state:
    left_, middle_= st.columns([4,1])
    for id,testcase in enumerate(st.session_state['testcases']):
            # Inject unique CSS for each button
            # with st.container(border=True):
            with st.expander(f'Scenario {id}', expanded=False):
                st.code(testcase,wrap_lines=True)
                # with middle_:
                #     # set_button_height(id, '15.0')
                if st.button('Validate', use_container_width=False, key=id):
                    # st.write('validated')
                    response = requests.get(validate_url, params={'testcase':testcase}).json()
                    st.code(response)


if right.button('Experiments', use_container_width=True):
    st.session_state['requirement'] = req
    nav_page("evolution")
    # response = requests.get(testcases_url, params={'requirement':req, 'sample':False}).json()
    # if response['STATUS'] == 'OK':
    #     st.write(response['testcases'])

# st.page_link("http://www.google.com", label="Google", icon="🌎")








