import streamlit as st
import streamlit.components.v1 as components
import mpld3
import matplotlib.pyplot as plt
# import pandas as pd
# import xarray
from erddapy import ERDDAP

"""
Streamlit prototype

Purpose: Test data visualization with Streamlit for python.
This script takes the plotting code from erddap_dataacess.ipynb and 
uses streamlit to create a web app displaying the plot.

To run this app locally in the browser, run the following command in the terminal
   streamlit run streamlit_mooring_app.py

Installation of streamlit is required. A virtual environment is recommended.
   pip install streamlit

Next steps:
 -Add more plots
 -Add interactive features
 -Test deployment to the community cloud to create a url link that can be shared publicly

Created by: 
Veronica Martinez 
8/9/23 
Ocean Hack Week project
"""


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
             "sea_water_practical_salinity"]

constraints = {"time>=": "max(time)-365"}

cioos_table = get_erddap_data(cioos_url, cioos_dataset,
                variables=variables,
                constraints=constraints,
                data_protocol="tabledap")

# Plot data
st.title('IOS_CTD_Moorings Data Visualization')

# Scatter plot
st.subheader('Scatter Plot')
fig, ax = plt.subplots()
cb = ax.scatter(cioos_table['time (UTC)'], cioos_table['sea_water_temperature (degC)'], c=cioos_table['sea_water_pressure (dbar)'], cmap='viridis')
fig.colorbar(cb, ax=ax)
my_xticks = cioos_table['time (UTC)']
plt.xticks(cioos_table['time (UTC)'], my_xticks)
fig_html = mpld3.fig_to_html(fig)       # makes plot interactive (zoom and pan)
components.html(fig_html, height=600)
# st.pyplot(fig)                        # use this for static plot

# # Line plot
# st.subheader('Line Plot')
# fig, ax = plt.subplots()
# ax.plot(data['Timestamp'], data['Value'])
# st.pyplot(fig)

