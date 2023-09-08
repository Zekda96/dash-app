from collections import namedtuple
import plotly.graph_objects as go
from params import prm


class Pitch:
    def __init__(self):
        # ALL DIMENSIONS IN m
        self.border_dimen = (
            3,
            3,
        )  # include a border arround of the field of width 3m
        self.meters_per_yard = 0.9144  # unit conversion from yards to meters
        self.half_pitch_length = prm.field_dim[0] / 2.0  # length of half pitch
        self.half_pitch_width = prm.field_dim[1] / 2.0  # width of half pitch
        self.signs = [-1, 1]
        # Soccer field dimensions typically defined in yards, so we need to
        # convert to meters
        self.goal_line_width = 8 * self.meters_per_yard
        self.box_width = 20 * self.meters_per_yard
        self.box_length = 6 * self.meters_per_yard
        self.area_width = 44 * self.meters_per_yard
        self.area_length = 18 * self.meters_per_yard
        self.penalty_spot = 12 * self.meters_per_yard
        self.corner_radius = 1 * self.meters_per_yard
        self.D_length = 8 * self.meters_per_yard
        self.D_radius = 10 * self.meters_per_yard
        self.D_pos = 12 * self.meters_per_yard
        self.centre_circle_radius = 10 * self.meters_per_yard

        self.point = namedtuple("point", ["x", "y"])
        self.centre = self.point(0.0, 0.0)

    def get_layout(
            self,
            time=None,
            frameID=None,
            frame_range=None,
            title=None,
            pitch_control=False,
    ):
        if pitch_control:
            field_markings_color = prm.pc["field_markings_color"]
            field_color = prm.pc["field_color"]
            title_color = prm.pc["title_color"]
        else:
            field_markings_color = prm.std["field_markings_color"]
            field_color = prm.std["field_color"]
            title_color = prm.std["title_color"]

        shapes = []

        mid_circle = dict(
            type="circle",
            x0=self.centre.x - self.centre_circle_radius,
            y0=self.centre.y - self.centre_circle_radius,
            x1=self.centre.x + self.centre_circle_radius,
            y1=self.centre.y + self.centre_circle_radius,
            line_color=field_markings_color,
            layer="below",
        )
        mid_line = dict(
            type="line",
            x0=self.centre.x,
            y0=self.centre.y - self.half_pitch_width,
            x1=self.centre.x,
            y1=self.centre.y + self.half_pitch_width,
            line_color=field_markings_color,
            layer="below",
        )
        mid_point = dict(
            type="circle",
            x0=self.centre.x - 0.4,
            y0=self.centre.y - 0.4,
            x1=self.centre.x + 0.4,
            y1=self.centre.y + 0.4,
            line_color=field_markings_color,
            fillcolor=field_markings_color,
            layer="below",
        )
        shapes.extend([mid_circle, mid_line, mid_point])

        for s in self.signs:
            # plot pitch boundary
            boundary1 = dict(
                type="line",
                x0=-self.half_pitch_length,
                y0=s * self.half_pitch_width,
                x1=self.half_pitch_length,
                y1=s * self.half_pitch_width,
                line_color=field_markings_color,
                layer="below",
            )

            boundary2 = dict(
                type="line",
                x0=s * self.half_pitch_length,
                y0=-self.half_pitch_width,
                x1=s * self.half_pitch_length,
                y1=self.half_pitch_width,
                line_color=field_markings_color,
                layer="below",
            )

            circle = dict(
                type="circle",
                x0=s
                * (self.centre.x + self.half_pitch_length - self.penalty_spot)
                - self.centre_circle_radius,
                y0=self.centre.y - self.centre_circle_radius,
                x1=s
                * (self.centre.x + self.half_pitch_length - self.penalty_spot)
                + self.centre_circle_radius,
                y1=self.centre.y + self.centre_circle_radius,
                line_color=field_markings_color,
                layer="below",
            )

            patch = dict(
                type="rect",
                x0=s * self.half_pitch_length,
                y0=-self.area_width / 2.0 - 1,
                x1=s * (self.half_pitch_length - self.area_length),
                y1=self.area_width / 2.0 + 1,
                line=dict(color=field_color, width=0),
                fillcolor=field_color,
                layer="below",
            )

            box = dict(
                type="rect",
                x0=s * self.half_pitch_length,
                y0=-self.area_width / 2.0,
                x1=s * (self.half_pitch_length - self.area_length),
                y1=self.area_width / 2.0,
                line=dict(color=field_markings_color, width=2),
                layer="below",
            )
            D = dict(
                type="rect",
                x0=s * self.half_pitch_length,
                y0=-self.box_width / 2.0,
                x1=s * (self.half_pitch_length - self.box_length),
                y1=self.box_width / 2.0,
                line=dict(color=field_markings_color, width=2),
                layer="below",
            )
            pen = dict(
                type="circle",
                x0=s * (self.half_pitch_length - self.penalty_spot) - 0.4,
                y0=-0.4,
                x1=s * (self.half_pitch_length - self.penalty_spot) + 0.4,
                y1=0.4,
                line_color=field_markings_color,
                fillcolor=field_markings_color,
                layer="below",
            )

            top_post = dict(
                type="rect",
                x0=s * self.half_pitch_length,
                y0=self.goal_line_width / 2.0 - 0.5,
                x1=s * (self.half_pitch_length - 0.5),
                y1=self.goal_line_width / 2.0 + 0.5,
                line=dict(color=field_markings_color, width=0),
                fillcolor=field_markings_color,
                layer="below",
            )

            bottom_post = dict(
                type="rect",
                x0=s * self.half_pitch_length,
                y0=-self.goal_line_width / 2.0 - 0.5,
                x1=s * (self.half_pitch_length - 0.5),
                y1=-self.goal_line_width / 2.0 + 0.5,
                line=dict(color=field_markings_color, width=0),
                fillcolor=field_markings_color,
                layer="below",
            )

            shapes.extend(
                [
                    boundary1,
                    boundary2,
                    circle,
                    patch,
                    box,
                    D,
                    pen,
                    top_post,
                    bottom_post,
                ]
            )

            # set axis limits
        xmax = prm.field_dim[0] / 2.0 + self.border_dimen[0]
        ymax = prm.field_dim[1] / 2.0 + self.border_dimen[1]

        layout = go.Layout(
            title={
                "text": title,
                "y": 0.98,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font_color": title_color,
                "font_size": 20,
            },
            hovermode="closest",
            autosize=True,
            width=prm.field_width,
            height=prm.field_height,
            plot_bgcolor=field_color,
            xaxis=go.layout.XAxis(
                range=[-xmax, xmax],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                visible=False,
            ),
            yaxis=go.layout.YAxis(
                range=[-ymax, ymax],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                visible=False,
                scaleanchor="x",
                scaleratio=1,
            ),
            margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0),
            legend=dict(
                x=0.1, y=0.993, orientation="h", bgcolor="rgba(0,0,0,0)"
            ),
        )

        layout["shapes"] = shapes

        # if title:
        #     layout["title_text"] = title

        return layout

    def plot_pitch(self, show=True):
        """Just generates an empty pitch.
        Store it in a fig object and add data to plot over it.
        """
        fig_dict = {"data": [], "layout": {}, "frames": []}

        fig_dict["layout"] = self.get_layout()

        fig = go.Figure(fig_dict)

        if show:
            fig.show()

        return fig
