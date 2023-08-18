import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def blank_diagram(fig_width=16, fig_height=9,
                  bg_color="antiquewhite", color="midnightblue"):
    fig = plt.figure(figsize=(fig_width / 2.54, fig_height / 2.54))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, fig_width)
    ax.set_ylim(0, fig_height)
    ax.set_facecolor(bg_color)

    ax.tick_params(bottom=False, top=False,
                   left=False, right=False)
    ax.tick_params(labelbottom=False, labeltop=False,
                   labelleft=False, labelright=False)

    ax.spines["top"].set_color(color)
    ax.spines["bottom"].set_color(color)
    ax.spines["left"].set_color(color)
    ax.spines["right"].set_color(color)
    ax.spines["top"].set_linewidth(4)
    ax.spines["bottom"].set_linewidth(4)
    ax.spines["left"].set_linewidth(4)
    ax.spines["right"].set_linewidth(4)

    return fig, ax

fig, ax = blank_diagram()
xy = (8, 6.5)
w = 2
h = 1

Box = Rectangle(xy, w, h, edgecolor="black", facecolor="white")
ax.add_patch(Box)
ax.text(xy[0] + w/2, xy[1] + h/2, "Compressor", fontsize=10, horizontalalignment="center", verticalalignment="center", color="black")

c = 0.1
Connector1 = Rectangle((xy[0] - c, xy[1] + h - 2*c), c, c, color="black")
Connector2 = Rectangle((xy[0] + w, xy[1] + h - 2*c), c, c, color="black")
Connector3 = Rectangle((xy[0] - c, xy[1] + c), c, c, color="black")
Connector4 = Rectangle((xy[0] + w, xy[1] + c), c, c, color="black")
ax.add_patch(Connector1)
ax.add_patch(Connector2)
ax.add_patch(Connector3)
ax.add_patch(Connector4)
ax.text(xy[0] + c, xy[1] + h - 3*c/2, " E1", fontsize=7, horizontalalignment="center", verticalalignment="center", color="black")
ax.text(xy[0] + w - c, xy[1] + h - 3*c/2, "E2 ", fontsize=7, horizontalalignment="center", verticalalignment="center", color="black")
ax.text(xy[0] + c, xy[1] + 3*c/2, " F1", fontsize=7, horizontalalignment="center", verticalalignment="center", color="black")
ax.text(xy[0] + w - c, xy[1] + 3*c/2, "F2 ", fontsize=7, horizontalalignment="center", verticalalignment="center", color="black")

ax.arrow(xy[0] - 3*c/2 - h/2, xy[1] + h - 3*c/2, h/2, 0, head_width=0.15, head_length=0.15, color="black")
# Draw arrows connecting them

plt.show()