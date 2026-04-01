import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_POINTS = 40
GIF_FILENAME = "jarvis_march.gif"
FPS = 12
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
HULL_COLOR = "#8be9fd"
FINAL_COLOR = "#50fa7b"
CANDIDATE_COLOR = "#f1fa8c"
LASER_COLOR = "#ff79c6"
ACTIVE_POINT = "#ffffff"
TEXT_COLOR = "#bd93f9"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance(p0, p1):
    return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2


def generate_frames(points):
    frames = []

    start_point = min(points, key=lambda p: p[0])
    hull = []

    current_point = start_point

    while True:
        hull.append(current_point)

        next_point = points[0]
        if next_point == current_point:
            next_point = points[1]

        for p in points:
            if p == current_point:
                continue

            frames.append(
                {
                    "hull": list(hull),
                    "current": current_point,
                    "candidate": next_point,
                    "checking": p,
                    "action": "sweep",
                }
            )

            cp = cross_product(current_point, next_point, p)

            if cp < 0 or (
                cp == 0
                and distance(current_point, p) > distance(current_point, next_point)
            ):
                next_point = p
                for _ in range(2):
                    frames.append(
                        {
                            "hull": list(hull),
                            "current": current_point,
                            "candidate": next_point,
                            "checking": None,
                            "action": "new_best",
                        }
                    )

        current_point = next_point

        if current_point == start_point:
            break

    hull.append(start_point)

    for _ in range(20):
        frames.append(
            {
                "hull": list(hull),
                "current": None,
                "candidate": None,
                "checking": None,
                "action": "done",
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


def update(frame_data):
    ax.clear()
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    hull = frame_data["hull"]
    current = frame_data["current"]
    candidate = frame_data["candidate"]
    checking = frame_data["checking"]
    action = frame_data["action"]

    ax.scatter(*zip(*points), color=POINT_COLOR, s=30, zorder=1)

    def plot_line(pts, color, lw=2, style="-"):
        if len(pts) > 1:
            px, py = zip(*pts)
            ax.plot(px, py, color=color, linewidth=lw, linestyle=style, zorder=2)

    current_hull_color = FINAL_COLOR if action == "done" else HULL_COLOR
    plot_line(hull, current_hull_color)

    if action != "done" and current:
        ax.scatter(
            current[0],
            current[1],
            color=ACTIVE_POINT,
            s=80,
            edgecolors=HULL_COLOR,
            linewidths=2,
            zorder=6,
        )

        if candidate:
            ax.plot(
                [current[0], candidate[0]],
                [current[1], candidate[1]],
                color=CANDIDATE_COLOR,
                linestyle="--",
                linewidth=2.5,
                zorder=4,
            )
            ax.scatter(
                candidate[0], candidate[1], color=CANDIDATE_COLOR, s=60, zorder=5
            )

        if action == "sweep" and checking:
            ax.plot(
                [current[0], checking[0]],
                [current[1], checking[1]],
                color=LASER_COLOR,
                linestyle=":",
                linewidth=1.5,
                zorder=3,
            )
            ax.scatter(
                checking[0], checking[1], color=LASER_COLOR, s=40, marker="+", zorder=4
            )

        if len(hull) == 1:
            bbox_props = dict(
                boxstyle="round,pad=0.6",
                fc=BG_COLOR,
                ec=CANDIDATE_COLOR,
                lw=1.5,
                alpha=0.9,
            )
            ax.text(
                np.mean(x),
                np.mean(y),
                "Jarvis March\nSweeping to find widest turn",
                color=CANDIDATE_COLOR,
                fontsize=12,
                ha="center",
                va="center",
                fontweight="bold",
                bbox=bbox_props,
                zorder=10,
            )


print(f"Generating {len(frames)} frames at {FPS} FPS...")
ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=1000 / FPS, repeat=False
)

print(f"Saving to {GIF_FILENAME}")
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done!")
