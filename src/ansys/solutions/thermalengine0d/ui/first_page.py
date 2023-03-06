# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the first step."""


from ansys.saf.glow.client.dashclient import DashClient
from dash_extensions.enrich import Input, Output, State, callback, dcc, html

from ansys.solutions.thermalengine0d.solution.definition import Thermalengine0DSolution
from ansys.solutions.thermalengine0d.solution.first_step import FirstStep


def layout(step: FirstStep):
    """Layout of the first step UI."""
    return html.Div(
        [
            dcc.Markdown("""#### First step""", className="display-3"),
            dcc.Markdown("""###### Configure and start your simulation.""", className="display-3"),
            html.Hr(className="my-2"),
            html.Br(),
            html.Div(["Simulation Duration (s): ", dcc.Input(id="first-arg", value=step.first_arg, type="number")]),
            html.Div(["Simulation Step (s): ", dcc.Input(id="second-arg", value=step.second_arg, type="number")]),
            html.Button("Run", id="calculate", n_clicks=0),
            html.P(id="result", children=f"Not started"),
        ]
    )


# This is an example callback which stores entered data and executes a method.
# This is the only place where user entered data is persisted in this Dash app.
# Notice that the project is referenced by a call to get_project and
# the url is a State argument to the callback
@callback(
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate(n_clicks, first_arg, second_arg, pathname):
    """Callback function to trigger the computation."""
    project = DashClient[Thermalengine0DSolution].get_project(pathname)
    step = project.steps.first_step
    step.first_arg = first_arg
    step.second_arg = second_arg
    step.calculate()
    return f"Completed in: {step.result}s"
