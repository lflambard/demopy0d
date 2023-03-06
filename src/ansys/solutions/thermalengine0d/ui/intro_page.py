# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the first step."""

import base64
import os
from pathlib import Path

import dash_bootstrap_components as dbc
from dash_extensions.enrich import dcc, html

from ansys.solutions.thermalengine0d.solution.intro_step import IntroStep


def layout(step: IntroStep):
    """Layout of the first step UI."""

    solution_workflow_sketch_encoded = base64.b64encode(
        open(
            os.path.join(Path(__file__).parent.absolute(), "assets", "Graphics", "Thermal-Engine-App.png"), "rb"
        ).read()
    )

    return html.Div(
        dbc.Container(
            [
                html.H1("Real Time Engine Models.", className="display-3", style={"font-size": "35px"}),
                html.P(
                    "Real time thermal engine models fulfil the needs of engine ECU development cycle.",
                    className="lead",
                    style={"font-size": "20px"},
                ),
                html.Hr(className="my-2"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dcc.Markdown(
                                            """
                                            **Description**

                                            These models are used for generation of environment models for control during  preliminary functional design, fast prototyping phases, and software validation.
                                            """,
                                            className="lead",
                                            style={
                                                "textAlign": "left",
                                                "marginLeft": "auto",
                                                "marginRight": "auto",
                                                "font-size": "15px",
                                            },
                                        ),
                                        html.Br(),
                                        dcc.Markdown(
                                            """
                                            **Customer goals**

                                            They allow users to test not only basic functional requirements of a control system but also performance requirements for pollution, driveability, consumption, combustion & torque, after-treatment.
                                            """,
                                            className="lead",
                                            style={
                                                "textAlign": "left",
                                                "font-size": "15px",
                                            },
                                        ),
                                        html.Br(),
                                        dcc.Markdown(
                                            """
                                            **Engineering goals**

                                            Easily represent different kinds of architectures, and polymorphic in order to represent the required range of frequencies or to fit to ECU performances.
                                            """,
                                            className="lead",
                                            style={
                                                "textAlign": "left",
                                                "font-size": "15px",
                                            },
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardImg(
                                                    src="data:image/png;base64,{}".format(
                                                        solution_workflow_sketch_encoded.decode()
                                                    ),
                                                ),
                                                dbc.CardFooter(""),
                                            ],
                                            style={"width": "50rem"},
                                        )
                                    ]
                                )
                            ],
                            width=6,
                        ),
                    ]
                ),
            ],
            fluid=True,
            className="py-3",
        ),
        className="p-3 bg-light rounded-3",
    )
