# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the second step."""


from ansys.saf.glow.client.dashclient import DashClient
from dash_extensions.enrich import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
from ansys.solutions.thermalengine0d.solution.definition import Thermalengine0DSolution
from ansys.solutions.thermalengine0d.solution.second_step import SecondStep
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def layout(step: SecondStep):
    """Layout of the second step UI."""
    return html.Div(
        [
            dcc.Markdown("""#### Data Analysis""", className="display-3"),
            dcc.Markdown("""###### Plotting of Simulation Results.""", className="display-3"),
            html.Hr(className="my-2"),
            html.P(id="result", children=f"Data Loading......"),
            html.Button("Export", id="export", n_clicks=0, disabled = True),
            dcc.Graph(id='graph-plot'),
            dcc.Graph(id='graph-plot2'),
            dcc.Graph(id='graph-plot3'),
            dcc.Graph(id='graph-plot4'),
            dcc.Graph(id='graph-plot5'),
            dcc.Graph(id='graph-plot6'),
        ]

    )


# This is an example callback which stores entered data and executes a method.
# This is the only place where user entered data is persisted in this Dash app.
# Notice that the project is referenced by a call to get_project and
# the url is a State argument to the callback
@callback(
    Output("result", "children"),
    Output("export", "disabled"),
    Output("graph-plot", "figure"),
    Output("graph-plot2", "figure"),
    Output("graph-plot3", "figure"),
    Output("graph-plot4", "figure"),
    Output("graph-plot5", "figure"),
    Output("graph-plot6", "figure"),
    Input("export", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def plots(n_clicks, pathname):
    """Callback function to trigger the computation."""
    project = DashClient[Thermalengine0DSolution].get_project(pathname)
    step = project.steps.second_step
    step_first = project.steps.first_step

    if n_clicks:
        step.exportcsv()
        message = "Loaded & Exported"
        return f"Data {message}", False, None, None, None, None, None, None
    else:
        if step_first.result_simu:
            step.plots()
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(go.Scatter(name='P1E', x=step.x_coord, y=step.y_coord['P1E']), row=1, col=1)
            fig.add_trace(go.Scatter(name='P1E set', x=step.x_coord, y=step.y_coord['P1E_ord']), row=1, col=1)
            fig.add_trace(go.Scatter(name='P2E', x=step.x_coord, y=step.y_coord['P2E']), row=1, col=1)
            fig.update_xaxes(title_text='time [s]')
            fig.update_yaxes(title_text='Pressure [Pa]')
            fig2 = px.line(x=step.x_coord, y=step.y_coord['VNT_act'])
            fig2.update_xaxes(title_text='time [s]')
            fig2.update_yaxes(title_text='VNT Position [0 - 1]')
            fig3 = make_subplots(rows=1, cols=1)
            fig3.add_trace(go.Scatter(name='T2C', x=step.x_coord, y=step.y_coord['T2C']), row=1, col=1)
            fig3.add_trace(go.Scatter(name='T1E', x=step.x_coord, y=step.y_coord['T1E']), row=1, col=1)
            fig3.add_trace(go.Scatter(name='T2E', x=step.x_coord, y=step.y_coord['T1T']), row=1, col=1)
            fig3.update_xaxes(title_text='time [s]')
            fig3.update_yaxes(title_text='Temperature [K]')
            fig4 = px.line(x=step.x_coord, y=step.y_coord['TqE'])
            fig4.update_xaxes(title_text='time [s]')
            fig4.update_yaxes(title_text='TqE [Nm]')
            fig5 = px.line(x=step.x_coord, y=step.y_coord['FAR'])
            fig5.update_xaxes(title_text='time [s]')
            fig5.update_yaxes(title_text='FAR [-]')
            fig6 = make_subplots(rows=1, cols=1)
            fig6.add_trace(go.Scatter(name='Qm1E', x=step.x_coord, y=step.y_coord['Qm1E']), row=1, col=1)
            fig6.add_trace(go.Scatter(name='Qm2E', x=step.x_coord, y=step.y_coord['Qm2E']), row=1, col=1)
            fig6.update_xaxes(title_text='time [s]')
            fig6.update_yaxes(title_text='Massic Flow [kg/s]')
            message = "Loaded"
            return f"Data {message}", False, fig, fig2, fig3, fig4, fig5, fig6
        else:
            message = "not available as no simulation was run"
            return f"Data {message}", True, None, None, None, None, None, None
