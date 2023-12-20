# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_site_names = sorted(spacex_df["Launch Site"].unique())

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites

                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{"label": "All Sites", "value": "ALL"}] +
                                            [{"label": f, "value": f} for f in launch_site_names],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000, step=1000, value=[0, 10000]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        successes_by_site = spacex_df.groupby("Launch Site")["class"].sum()
        site_names = [i for i, _ in successes_by_site.items()]

        fig = px.pie(successes_by_site, values='class',
                     names=site_names,
                     title='Total Successful Launches by Site')
        return fig
    elif entered_site in launch_site_names:
        # return the outcomes piechart for a selected site
        launches_at_site = spacex_df[spacex_df["Launch Site"] == entered_site]
        success_data = launches_at_site.groupby("class").size().to_frame()
        success_data.columns = ["class"]
        successes_names = ["Failure", "Success"]
        fig = px.pie(success_data, values='class',
                     names=successes_names,
                     title='Success rate for site {}'.format(entered_site))
        return fig
    else:
        raise Exception("Unknown site - {}".format(entered_site))


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(launch_site, payload_range):
    if launch_site == 'ALL':
        filtered_data = spacex_df
        title = "Correlation between payload and success for all sites"
    elif launch_site in launch_site_names:
        # return the outcomes piechart for a selected site
        filtered_data = spacex_df[spacex_df["Launch Site"] == launch_site]
        title = "Correlation between payload and success for {}".format(launch_site)
    else:
        raise Exception("Unknown site - {}".format(launch_site))
    filtered_data = filtered_data[(filtered_data['Payload Mass (kg)'] > payload_range[0]) & 
                                  (filtered_data['Payload Mass (kg)'] < payload_range[1])]
    return px.scatter(filtered_data, x='Payload Mass (kg)', y='class', title=title, color="Booster Version Category")

# Run the app
if __name__ == '__main__':
    app.run_server()
