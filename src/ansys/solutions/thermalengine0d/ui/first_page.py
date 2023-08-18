# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the first step."""


from ansys.saf.glow.client.dashclient import DashClient
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
from ansys.solutions.thermalengine0d.solution.definition import Thermalengine0DSolution
from ansys.solutions.thermalengine0d.solution.first_step import FirstStep
from ansys.solutions.thermalengine0d.solution.config_step import ConfigStep
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def layout(step: FirstStep):
    """Layout of the first step UI."""
    return html.Div(
        dbc.Container(
            [
                dcc.Markdown("""#### Simulation""", className="display-3"),
                dcc.Markdown("""###### Run your simulation.""", className="display-3"),
                html.Hr(className="my-2"),
                html.Button("Run", id="calculate", n_clicks=0),
                html.P(id="result", children=f"Not started"),
            ],
        ),
    )


# This is an example callback which stores entered data and executes a method.
# This is the only place where user entered data is persisted in this Dash app.
# Notice that the project is referenced by a call to get_project and
# the url is a State argument to the callback
@callback(
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate(n_clicks, pathname):
    """Callback function to trigger the computation."""
    project = DashClient[Thermalengine0DSolution].get_project(pathname)

    if n_clicks:
        step = project.steps.first_step
        config_step = project.steps.config_step
        if config_step.control:
            step.calculate()
            return f"Completed in: {step.result}s"
        else:
            return f"Simulation cannot run as there is no configuration available."
    else:
        raise PreventUpdate

