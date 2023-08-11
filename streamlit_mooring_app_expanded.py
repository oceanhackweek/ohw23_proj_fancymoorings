import streamlit as st
import matplotlib.pyplot as plt
from erddapy import ERDDAP
import plotly.express as px
from datetime import datetime

# """
# Streamlit prototype
#
# Purpose: Test data visualization with Streamlit for python.
# This script takes the plotting code from erddap_dataacess.ipynb and
# uses streamlit to create a web app displaying the plot.
#
# To run this app locally in the browser, run the following command in the terminal
#    streamlit run streamlit_mooring_app.py
#
# Installation of streamlit is required. A virtual environment is recommended.
#    pip install streamlit
#
# Next steps:
#  -Add more interactive features
#
# Created by:
# Veronica Martinez
# 8/10/23
# Ocean Hack Week project
# """


def get_erddap_data(erddap_url, dataset, data_protocol="griddap", variables=None, constraints=None):
    """
    Function: get_erddap_data
    This function uses the erddapy python library to access data from ERDDAP servers,
    and to return it to users in convenient formats for python users.
    Data can be pulled from "tabledap" or "griddap" formats, with different
    output types, depending on the dap type.

    Inputs:
    erddap_url    - The url address of the erddap server to pull data from
    variables     - The selected variables within the dataset.
    data_protocol - The erddap data protocol for the chosen dataset.
                    Options include "tabledap" or "griddap"
                    The default option is given as "griddap"
    dataset       - The ID for the relevant dataset on the erddap server
                    If no variables are given, it is assumed that all variables
                    will be pulled.
    constraints   - These are set by the user to help restrict the data pull
                    to only the area and timeframe of interest.
                    If no constraints are given, all data in a dataset is pulled.
                    Constraints should be given as a dictionary, where
                    each entry is a bound and/or selection of a specific axis variable
                    Exs. {"longitude<=": "min(longitude)+10", "longitude>=": "0"}
                         {"longitude=": "140", "time>=": "max(time)-30"}

    Outputs:
    erddap_data   - This variable contains the pulled data from the erddap server.
                    If the data_protocol is "griddap",  then erddap_data is an xarray dataset
                    If the data_protocol is "tabledap", then erddap_data is a pandas dataframe
    """



    ############################################
    # Set-up the connection to the ERDDAP server
    ############################################

    # Connect to the erddap server
    e = ERDDAP(server=erddap_url, protocol=data_protocol, response='csv')

    # Identify the dataset of interest
    e.dataset_id = dataset

    #########################################
    # Pull the data, based upon protocol type
    #########################################

    # GRIDDAP Protocol
    if data_protocol == "griddap":

        # Initialize the connection
        e.griddap_initialize()

        # Update the constraints
        if constraints is not None:
            e.constraints.update(constraints)
            e.griddap_initialize()

        # Update the selection of the variables
        if variables is not None:
            e.variables = variables

        erddap_data = e.to_xarray()

    # TABLEDAP Protocol
    elif data_protocol == "tabledap":

        # Update the constraints
        if constraints is not None:
            e.constraints = constraints

        # Update the selection of the variables
        if variables is not None:
            e.variables = variables

        erddap_data = e.to_pandas()

    # Invalid protocol given
    else:
        print('Invalid ERDDAP protocol. Given protocol is: ' + data_protocol)
        print('Valid protocols include "griddap" or "tabledap". Please restart and try again with a valid protocol')
        erddap_data = None

    #############################
    return erddap_data


# Get data
cioos_url = 'https://data.cioospacific.ca/erddap'
cioos_dataset = 'IOS_CTD_Moorings'

variables = ["time",
             "sea_water_pressure",
             "sea_water_temperature",
             "sea_water_practical_salinity",
             "TEMPST01",
             "depth",
             "longitude",
             "latitude",
             "filename"]

constraints = {"time>=":datetime(2022,7,1).strftime('%Y-%m-%dT%H:%M:%SZ'),
               "longitude>=": -128.975,
               "longitude<=": -121.975,
               "latitude>=": 49.1,
               "latitude<=": 49.3}

data = get_erddap_data(cioos_url, cioos_dataset,
                variables=variables,
                constraints=constraints,
                data_protocol="tabledap")


# Plot data
st.title('IOS_CTD_Moorings Data Visualization')

# Interactive Plot
st.subheader('Interactive Scatter Plot')
st.write('Location:  (49.1 - 49.3 & 126 - 126.7)')
st.write('Time frame:  2022-07-01 to 2022-07-21')

# # Streamlit widgets for interactive filtering
selected_variable = st.selectbox('Select Variable', ('sea_water_temperature (degC)', 'sea_water_pressure (dbar)',
                                                     'sea_water_practical_salinity (PSS-78)'))
plot = px.scatter(data, x=data['time (UTC)'], y=selected_variable)
st.plotly_chart(plot)

# Static Scatter plot
# Get smaller dataset
constraints = {"time>=": "max(time)-365"}
data = get_erddap_data(cioos_url, cioos_dataset,
                variables=variables,
                constraints=constraints,
                data_protocol="tabledap")

st.subheader('Static Scatter Plot')
st.write('Time frame:  2022-07-21')
fig, ax = plt.subplots()
cb = ax.scatter(data['time (UTC)'], data['sea_water_temperature (degC)'], c=data['sea_water_pressure (dbar)'], cmap='viridis')
ax.set_xlabel('time (UTC)')
ax.set_ylabel('sea_water_temperature (degC)')
fig.colorbar(cb, ax=ax)
st.pyplot(fig)

# Display data table
df_subset=data.loc[0:,['time (UTC)','sea_water_temperature (degC)', 'sea_water_pressure (dbar)']]
st.dataframe(df_subset)
