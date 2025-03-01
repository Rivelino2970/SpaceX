# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np  # For jitter in scatter plot

# Read the SpaceX data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Get dynamic launch site options for the dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,  # Dynamic options
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart for success/failure counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Slider for payload range selection
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(min_payload + i * (max_payload - min_payload) / 4): 
               f'{int(min_payload + i * (max_payload - min_payload) / 4)}' 
               for i in range(5)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter chart for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Show total success launches for all sites
        fig = px.pie(spacex_df, values='class', names='Launch Site', 
                     title='Total Success Launches by Site')
    else:
        # Show success/failure ratio for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class', 
                     title=f'Success/Failure Ratio for {entered_site}')
    return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    # Filter by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Add jitter to class values to avoid overlapping points
    filtered_df['jittered_class'] = filtered_df['class'] + \
        np.random.uniform(-0.1, 0.1, size=len(filtered_df))
    
    # Filter by site if a specific site is selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='jittered_class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=f'Payload vs. Launch Outcome for {entered_site if entered_site != "ALL" else "All Sites"}',
        labels={'jittered_class': 'Launch Outcome'}
    )
    
    # Improve y-axis labels
    fig.update_layout(
        yaxis={
            'tickvals': [0, 1],
            'ticktext': ['Failure', 'Success']
        }
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()