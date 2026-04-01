import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_POINTS = 40
GIF_FILENAME = "monotone_chain.gif"
FPS = 4
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
HULL_COLOR = "#8be9fd"
FINAL_COLOR = "#50fa7b"
CHECK_COLOR = "#f1fa8c"
BAD_COLOR = "#ff5555"
ACTIVE_POINT = "#ffffff"
TEXT_COLOR = "#bd93f9"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def generate_frames(points):
    """
    Runs Monotone Chain and yields the state at every step.
    """
    points = sorted(points, key=lambda p: (p[0], p[1]))
    frames = []

    lower = []
    for p in points:
        frames.append(
            {
                "lower": list(lower),
                "upper": [],
                "active": p,
                "action": "eval",
                "phase": "lower_build",
            }
        )

        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
            for _ in range(2):
                frames.append(
                    {
                        "lower": list(lower),
                        "upper": [],
                        "active": p,
                        "action": "pop",
                        "phase": "lower_build",
                    }
                )
            lower.pop()

        lower.append(p)
        frames.append(
            {
                "lower": list(lower),
                "upper": [],
                "active": None,
                "action": "add",
                "phase": "lower_build",
            }
        )

    for _ in range(6):
        frames.append(
            {
                "lower": list(lower),
                "upper": [],
                "active": None,
                "action": "pause",
                "phase": "transition",
            }
        )

    upper = []
    for p in reversed(points):
        frames.append(
            {
                "lower": lower,
                "upper": list(upper),
                "active": p,
                "action": "eval",
                "phase": "upper_build",
            }
        )

        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
            for _ in range(2):
                frames.append(
                    {
                        "lower": lower,
                        "upper": list(upper),
                        "active": p,
                        "action": "pop",
                        "phase": "upper_build",
                    }
                )
            upper.pop()

        upper.append(p)
        frames.append(
            {
                "lower": lower,
                "upper": list(upper),
                "active": None,
                "action": "add",
                "phase": "upper_build",
            }
        )

    for _ in range(12):
        frames.append(
            {
                "lower": lower,
                "upper": upper,
                "active": None,
                "action": "done",
                "phase": "done",
            }
        )

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

center_x = np.mean(x)
center_y = np.mean(y)


def update(frame_data):
    ax.clear()
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    lower = frame_data["lower"]
    upper = frame_data["upper"]
    active = frame_data["active"]
    action = frame_data["action"]
    phase = frame_data["phase"]

    ax.scatter(*zip(*points), color=POINT_COLOR, s=30, zorder=1)

    def plot_line(pts, color, lw=2, style="-"):
        if len(pts) > 1:
            px, py = zip(*pts)
            ax.plot(px, py, color=color, linewidth=lw, linestyle=style, zorder=2)

    if phase == "lower_build":
        plot_line(lower, HULL_COLOR)

    elif phase == "transition":
        plot_line(lower, FINAL_COLOR)
        bbox_props = dict(
            boxstyle="round,pad=0.6", fc=BG_COLOR, ec=FINAL_COLOR, lw=1.5, alpha=0.9
        )
        ax.text(
            center_x,
            center_y,
            "Lower Hull Complete\nStarting Upper...",
            color=TEXT_COLOR,
            fontsize=14,
            ha="center",
            va="center",
            fontweight="bold",
            bbox=bbox_props,
            zorder=10,
        )

    elif phase == "upper_build":
        plot_line(lower, FINAL_COLOR)
        plot_line(upper, HULL_COLOR)

    elif phase == "done":
        plot_line(lower, FINAL_COLOR)
        plot_line(upper, FINAL_COLOR)

    active_hull = upper if phase == "upper_build" else lower

    if action == "eval" and len(active_hull) > 0 and active:
        last_point = active_hull[-1]
        ax.plot(
            [last_point[0], active[0]],
            [last_point[1], active[1]],
            color=CHECK_COLOR,
            linestyle="--",
            linewidth=2,
            zorder=3,
        )

    elif action == "pop" and len(active_hull) >= 2 and active:
        p1, p2 = active_hull[-2], active_hull[-1]
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

    if active:
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

print(f"Saving to {GIF_FILENAME} (this may take a few seconds)...")
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done!")
