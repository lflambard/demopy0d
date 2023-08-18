# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the configuration step."""


from ansys.saf.glow.client.dashclient import DashClient
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
from ansys.solutions.thermalengine0d.solution.definition import Thermalengine0DSolution
from ansys.solutions.thermalengine0d.solution.config_step import ConfigStep
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def layout(step: ConfigStep):
    """Layout of the configuration step UI."""
    if step.control:
       text_message = "A configuration is already available"
    else:
        text_message = "No configuration downloaded"

    return html.Div(
        dbc.Container(
            [
                dcc.Markdown("""#### Simulation Preparation""", className="display-3"),
                dcc.Markdown("""###### Configure your model.""", className="display-3"),
                html.Hr(className="my-2"),
                html.Button("Configure", id="loadfile", n_clicks=0),
                html.P(id="configure_text", children=f"{text_message}"),
                html.Br(),
                dcc.Markdown("""###### Configure your simulation.""", className="display-3"),
                html.Hr(className="my-2"),
                html.Div(["Simulation Duration (s): ", dcc.Input(id="first-arg", value=step.first_arg, type="number", style={"background-color": "black", "color": "white"})]),
                html.Div(["Simulation Step (s): ", dcc.Input(id="second-arg", value=step.second_arg, type="number", style={"margin-left": "30px", "background-color": "black", "color": "white"}), ]),
                html.Div(["Result Sample Time (s): ", dcc.Input(id="third-arg", value=step.third_arg, type="number", style={"margin-left": "3px", "background-color": "black", "color": "white"})],),
                html.Br(),
                html.Div(["Time for Nset (s): ", dcc.Input(id="x-N", value=step.x_N, type="text", style={"background-color": "black", "color": "white"}),"time for Pedal Position (s): ", dcc.Input(id="x-pps", value=step.x_pps, type="text", style={"background-color": "black", "color": "white"})],),
                html.Div(["Nset (rpm): ", dcc.Input(id="y-N", value=step.y_N, type="text", style={"margin-left": "41px", "background-color": "black", "color": "white"}),"Pedal Position (0 - 1): ", dcc.Input(id="y-pps", value=step.y_pps,type="text", style={"margin-left": "35px", "background-color": "black", "color": "white"})],),
                dcc.Graph(id='graph-plot'),
            ],
        ),
    )


# This is an example callback which stores entered data and executes a method.
# This is the only place where user entered data is persisted in this Dash app.
# Notice that the project is referenced by a call to get_project and
# the url is a State argument to the callback
@callback(
    Output("configure_text", "children"),
    Output("graph-plot", "figure"),
    Output("x-N", "value"),
    Output("y-N", "value"),
    Output("x-pps", "value"),
    Output("y-pps", "value"),
    Input("loadfile", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    State("third-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def configure(n_clicks, first_arg, second_arg, third_arg, pathname):
    """Callback function to trigger the computation."""
    project = DashClient[Thermalengine0DSolution].get_project(pathname)
    step = project.steps.config_step
    fig = make_subplots(rows=1, cols=2)
    if n_clicks:
        step.configure()
        fig.add_trace(go.Scatter(name='N set [rpm]', x=eval(step.x_N), y=eval(step.y_N)), row=1, col=1)
        fig.add_trace(go.Scatter(name='Pedal Position set [0 - 1]', x=eval(step.x_pps), y=eval(step.y_pps)), row=1, col=2)
        fig.update_xaxes(title_text='time [s]')
        return f"New configuration downloaded", fig, step.x_N, step.y_N,step.x_pps,step.y_pps
    else:
        raise PreventUpdate

@callback(
    Output("configure_text", "children"),
    Output("graph-plot", "figure"),
    Input("first-arg", "value"),
    Input("second-arg", "value"),
    Input("third-arg", "value"),
    Input("x-N", "value"),
    Input("y-N", "value"),
    Input("x-pps", "value"),
    Input("y-pps", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def simulation(first_arg, second_arg, third_arg, x_N, y_N, x_pps, y_pps, pathname):
    """Callback function to trigger the computation."""
    project = DashClient[Thermalengine0DSolution].get_project(pathname)

    step = project.steps.config_step
    step.first_arg = first_arg
    step.second_arg = second_arg
    step.third_arg = third_arg
    step.x_N = x_N
    step.y_N = y_N
    step.x_pps = x_pps
    step.y_pps = y_pps

    fig = make_subplots(rows=1, cols=2)
    if step.control:
        fig.add_trace(go.Scatter(name='N set [rpm]', x=eval(step.x_N), y=eval(step.y_N)), row=1, col=1)
        fig.add_trace(go.Scatter(name='Pedal Position set [0 - 1]', x=eval(step.x_pps), y=eval(step.y_pps)), row=1, col=2)
        fig.update_xaxes(title_text='time [s]')
        text_message = "A configuration is already available"
    else:
        text_message = "No configuration downloaded"

    return f"{text_message}", fig
