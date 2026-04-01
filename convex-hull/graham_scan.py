import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

NUM_POINTS = 40
GIF_FILENAME = "graham_scan.gif"
FPS = 4
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
HULL_COLOR = "#8be9fd"
FINAL_COLOR = "#50fa7b"
CHECK_COLOR = "#f1fa8c"
BAD_COLOR = "#ff5555"
ACTIVE_POINT = "#ffffff"
PIVOT_COLOR = "#ffb86c"
TEXT_COLOR = "#bd93f9"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def polar_angle(p0, p1):
    return math.atan2(p1[1] - p0[1], p1[0] - p0[0])


def distance(p0, p1):
    return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2


def generate_frames(points):
    frames = []

    p0 = min(points, key=lambda p: (p[1], p[0]))
    frames.append({"hull": [], "active": p0, "action": "find_pivot", "p0": p0})

    sorted_points = sorted(
        [p for p in points if p != p0],
        key=lambda p: (polar_angle(p0, p), distance(p0, p)),
    )

    hull = [p0, sorted_points[0]]
    frames.append({"hull": list(hull), "active": None, "action": "add", "p0": p0})

    for p in sorted_points[1:]:
        frames.append({"hull": list(hull), "active": p, "action": "eval", "p0": p0})

        while len(hull) > 1 and cross_product(hull[-2], hull[-1], p) <= 0:
            for _ in range(2):
                frames.append(
                    {"hull": list(hull), "active": p, "action": "pop", "p0": p0}
                )
            hull.pop()

        hull.append(p)
        frames.append({"hull": list(hull), "active": None, "action": "add", "p0": p0})

    hull.append(p0)

    for _ in range(12):
        frames.append({"hull": list(hull), "active": None, "action": "done", "p0": p0})

    return frames


np.random.seed(42)
angles = np.random.uniform(0, 2 * np.pi, NUM_POINTS)
radii = np.random.uniform(0, 10, NUM_POINTS)
x = radii * np.cos(angles)
y = radii * np.sin(angles)
points = list(zip(x, y))

frames = generate_frames(points)

fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG_COLOR)
plt.subplots_adjust(left=0, right=1, bottom=0, top=1)

padding = 2
xlim = (min(x) - padding, max(x) + padding)
ylim = (min(y) - padding, max(y) + padding)


def update(frame_data):
    ax.clear()
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    hull = frame_data["hull"]
    active = frame_data["active"]
    action = frame_data["action"]
    p0 = frame_data["p0"]

    ax.scatter(*zip(*points), color=POINT_COLOR, s=30, zorder=1)

    if p0:
        ax.scatter(p0[0], p0[1], color=PIVOT_COLOR, s=100, marker="*", zorder=6)

    def plot_line(pts, color, lw=2, style="-"):
        if len(pts) > 1:
            px, py = zip(*pts)
            ax.plot(px, py, color=color, linewidth=lw, linestyle=style, zorder=2)

    current_hull_color = FINAL_COLOR if action == "done" else HULL_COLOR
    plot_line(hull, current_hull_color)

    if action == "find_pivot":
        bbox_props = dict(
            boxstyle="round,pad=0.6", fc=BG_COLOR, ec=PIVOT_COLOR, lw=1.5, alpha=0.9
        )
        ax.text(
            np.mean(x),
            np.mean(y),
            "1. Find Lowest Point (Pivot)\n2. Sort by Polar Angle",
            color=PIVOT_COLOR,
            fontsize=12,
            ha="center",
            va="center",
            fontweight="bold",
            bbox=bbox_props,
            zorder=10,
        )

    if action == "eval" and len(hull) > 0 and active:
        ax.plot(
            [p0[0], active[0]],
            [p0[1], active[1]],
            color=PIVOT_COLOR,
            linestyle=":",
            linewidth=1,
            alpha=0.5,
            zorder=2,
        )

        last_point = hull[-1]
        ax.plot(
            [last_point[0], active[0]],
            [last_point[1], active[1]],
            color=CHECK_COLOR,
            linestyle="--",
            linewidth=2,
            zorder=3,
        )

    elif action == "pop" and len(hull) >= 2 and active:
        p1, p2 = hull[-2], hull[-1]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=BAD_COLOR, linewidth=3, zorder=4)
        ax.plot(
            [p2[0], active[0]],
            [p2[1], active[1]],
            color=BAD_COLOR,
            linestyle="--",
            linewidth=2,
            zorder=4,
        )
        ax.scatter(
            p2[0], p2[1], color=BAD_COLOR, s=120, marker="x", linewidths=2, zorder=5
        )

    if active and action != "find_pivot":
        ax.scatter(
            active[0],
            active[1],
            color=ACTIVE_POINT,
            s=60,
            edgecolors=CHECK_COLOR,
            linewidths=1.5,
            zorder=5,
        )


print(f"Generating {len(frames)} frames at {FPS} FPS...")
ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=1000 / FPS, repeat=False
)

print(f"Saving to {GIF_FILENAME}...")
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done!")
