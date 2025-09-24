import streamlit as st
import streamlit.components.v1 as components
from mlflow.tracking import MlflowClient
import redis
import pandas as pd
import ast
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import numpy as np

st.set_page_config(layout="wide")
env = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

st.header("Explore and figure out the variables causing high failure rates")

st.link_button('Go to Experiments Tracking','http://localhost:5000')

client = MlflowClient(tracking_uri="http://localhost:5000")
experiments = client.search_experiments()
experiments = {exp.name : exp for exp in experiments}

exp_name = st.selectbox("Choose the Experiment", experiments.keys())
experiment = experiments[exp_name]

experiment_id = experiment.experiment_id
runs = client.search_runs(experiment_ids=[experiment_id])

# with st.expander(experiment.name, expanded=True):
    # st.code(experiment.name)

# left , middle, right = st.tabs(['Test Case Data','Model Predictions', 'Failure Explanations'])

# with left:
X = []
y = []
for run in runs:
    data = {
                "run_id": run.info.run_id,
                "parameters": run.data.params,
                "metrics": run.data.metrics,
                "tags": run.data.tags
            }
    if data['parameters'] and data['metrics']:
        params = data['parameters']['params']
        metrics = data['metrics']

        X.append(ast.literal_eval(params))
        y.append(metrics["Percentage of testcase passed"])

DATA = pd.DataFrame(X)
DATA['Success Rate'] = y
DATA['Success Rate'] = DATA['Success Rate']/100.

# st.dataframe(DATA, use_container_width=True) 

start_pct, end_pct = st.select_slider(
                                        "Select a range of Success Rate",
                                        options= list(np.arange(0,1.1,.1)),
                                        value=(0, .1),
                                    )

data_ = DATA[(DATA['Success Rate'] <= end_pct) & (DATA['Success Rate'] >= start_pct)]
st.dataframe(data_, use_container_width=True) 

categorical_columns = ["pedestrian", "dress", "direction", "distance","fog_density"]

for col in categorical_columns:
    data_[col] = data_[col].astype('category')
# Melt the DataFrame to create a single column for all the categorical variables
data_melted = pd.melt(data_, id_vars=['Success Rate'], value_vars=categorical_columns,
                    var_name='Category', value_name='Category Value')

# Streamlit header
st.subheader("Boxplot of Success Rate by Categorical Variables")

# Plotting
plt.figure(figsize=(12, 4))

# Create a boxplot of Success Rate grouped by Category and Category Value
sns.boxplot(x='Category Value', y='Success Rate', hue='Category', data=data_melted, palette='Set2')
# Adjust the legend location outside the plot
plt.legend().set_visible(False)
# Add labels and title
plt.title('Boxplot of Success Rate by Categorical Variables')
plt.xlabel('Category Value')
plt.ylabel('Success Rate')
# plt.ylim(-.1, 1.2)

# Show the plot in Streamlit
st.pyplot(plt)

plt.figure(figsize=(12, 4))
# Create a violin plot of Success Rate grouped by Category and Category Value
sns.violinplot(x='Category Value', y='Success Rate', hue='Category', data=data_melted, palette='Set2', split=False)

# Add labels and title
plt.title('Violin Plot of Success Rate by Categorical Variables')
plt.xlabel('Category Value')
plt.ylabel('Success Rate')
# plt.ylim(-.1, 1.2)

# Adjust the legend location outside the plot
plt.legend(title='Category', bbox_to_anchor=(0.5, -.3), loc='center', ncol=len(categorical_columns))

# Show the plot in Streamlit
st.pyplot(plt)

# with middle:

#     if st.button('Train Model'):

#         # Encode categorical features
#         # label_encoders = {}
#         for col in ["pedestrian", "dress", "direction", "distance"]:
#             DATA[col] = DATA[col].astype('category')
#             # le = LabelEncoder()
#             # DATA[col] = le.fit_transform(DATA[col])
#             # label_encoders[col] = le  # Save encoders if needed for future mapping
        
#         DATA['fog_density'] = DATA['fog_density'].apply(lambda x : int(x))

#         # Split into features (X) and target (y)
#         X = DATA.drop(columns=["Success Rate"])
#         y =DATA["Success Rate"]

#         # Split data into training and testing sets (80% train, 20% test)
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#         # Convert data into LightGBM dataset format
#         train_data = lgb.Dataset(X, label=y)
#         valid_data = lgb.Dataset(X, label=y, reference=train_data)  # Validation dataset

#         # Set LightGBM parameters
#         params = {
#             "objective": "regression",
#             "metric": "rmse",
#             "boosting_type": "gbdt",
#             "learning_rate": 0.1,
#             "num_leaves": 31,
#             "early_stopping_round": 10
#         }

#         # Train the LightGBM model with early stopping
#         model = lgb.train(
#             params,
#             train_data,
#             valid_sets=[train_data, valid_data],  # Provide both training and validation sets
#             valid_names=["train", "valid"],  # Assign names for monitoring
#             num_boost_round=100
#             # early_stopping_rounds=10  # Stops if validation loss stops improving
#         )

#         # Make predictions
#         y_pred = model.predict(X_test)
#         train_pred = model.predict(X_train)
#         pred = model.predict(X)

#         # Evaluate performance
#         rmse = mean_squared_error(y_test, y_pred, squared=False)
#         print(f"Root Mean Squared Error (RMSE): {rmse}")

#         # Show feature importance
#         # st.pyplot(lgb.plot_importance(model), use_container_width=False)

#         # Plot Actual vs. Predicted values
#         fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(12, 6))


        
#         # sns.scatterplot(x=y_test, y=y_pred, color="blue", label="Predictions", ax=ax)
#         sns.scatterplot(x=y, y=pred, color="green", label="Predictions", ax=ax)
#         sns.lineplot(x=y, y=y, color="red", linestyle="--", label="Perfect Fit", ax=ax)  # Ideal line
        
#         ax.set_xlabel("Actual Success Rate")
#         ax.set_ylabel("Predicted Success Rate")
#         ax.set_title("Actual vs Predicted Success Rate")
#         ax.legend()
#         ax.grid(True)

#         st.pyplot(fig, use_container_width=False)

# with right:

#     if st.button('Explain'):

#         # Visualize the first decision tree in the model
#         # Plot the first tree
#         fig, ax = plt.subplots(figsize=(20, 10))
#         lgb.plot_tree(model, tree_index=0, figsize=(20, 10), show_info=['split_gain', 'internal_value', 'internal_count'], ax=ax)

#         # Show the plot in Streamlit
#         st.pyplot(fig)



#         # # Create a SHAP explainer
#         # explainer = shap.TreeExplainer(model)
#         # # Calculate SHAP values
#         # shap_values = explainer.shap_values(X)

#         # # Show a summary plot of SHAP values
#         # st.subheader('SHAP Summary Plot')
#         # fig, ax = plt.subplots(figsize=(10, 6))
#         # shap.summary_plot(shap_values, X, plot_type="bar", show=False)
#         # st.pyplot(fig)

#         # # Show force plot for the first instance
#         # st.subheader('SHAP Force Plot (for the first instance)')
#         # shap.initjs()
#         # fig = shap.force_plot(explainer.expected_value, shap_values[0], X[0], matplotlib=True)
#         # st.pyplot(fig)

