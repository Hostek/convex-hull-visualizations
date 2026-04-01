import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_POINTS = 40
GIF_FILENAME = "quick_hull.gif"
FPS = 5
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
DISCARDED_COLOR = "#222222"
HULL_COLOR = "#8be9fd"
FINAL_COLOR = "#50fa7b"
TRIANGLE_COLOR = "#bd93f9"
ACTIVE_POINT = "#ffb86c"
TEXT_COLOR = "#ffffff"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def dist_to_line(p, a, b):
    return abs((p[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (p[0] - a[0]))


def generate_frames(points):
    frames = []
    final_edges = []
    discarded = []

    pts = sorted(points, key=lambda p: (p[0], p[1]))
    A = pts[0]
    B = pts[-1]

    s1 = [p for p in pts if cross_product(A, B, p) > 0]
    s2 = [p for p in pts if cross_product(B, A, p) > 0]

    inside = [p for p in pts if p not in s1 and p not in s2 and p != A and p != B]
    discarded.extend(inside)

    frames.append(
        {
            "final": [],
            "active_line": (A, B),
            "triangle": None,
            "furthest": None,
            "discarded": list(discarded),
            "msg": "Find Min/Max X",
        }
    )

    def find_hull(sk, P, Q, side_name):
        if not sk:
            final_edges.append((P, Q))
            frames.append(
                {
                    "final": list(final_edges),
                    "active_line": None,
                    "triangle": None,
                    "furthest": None,
                    "discarded": list(discarded),
                    "msg": f"Edge Locked",
                }
            )
            return

        C = max(sk, key=lambda p: dist_to_line(p, P, Q))

        frames.append(
            {
                "final": list(final_edges),
                "active_line": (P, Q),
                "triangle": None,
                "furthest": C,
                "discarded": list(discarded),
                "msg": "Finding Furthest Point",
            }
        )

        frames.append(
            {
                "final": list(final_edges),
                "active_line": (P, Q),
                "triangle": (P, C, Q),
                "furthest": C,
                "discarded": list(discarded),
                "msg": "Forming Triangle",
            }
        )

        s0 = [p for p in sk if cross_product(P, C, p) > 0]
        s1 = [p for p in sk if cross_product(C, Q, p) > 0]

        inside = [p for p in sk if p not in s0 and p not in s1 and p != C]
        discarded.extend(inside)

        frames.append(
            {
                "final": list(final_edges),
                "active_line": None,
                "triangle": (P, C, Q),
                "furthest": C,
                "discarded": list(discarded),
                "msg": "Discarding Inner Points",
            }
        )

        find_hull(s0, P, C, side_name)
        find_hull(s1, C, Q, side_name)

    find_hull(s1, A, B, "Top")
    find_hull(s2, B, A, "Bottom")

    for _ in range(12):
        frames.append(
            {
                "final": list(final_edges),
                "active_line": None,
                "triangle": None,
                "furthest": None,
                "discarded": list(discarded),
                "msg": "QuickHull Complete!",
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

    final_edges = frame_data["final"]
    active_line = frame_data["active_line"]
    triangle = frame_data["triangle"]
    furthest = frame_data["furthest"]
    discarded = frame_data["discarded"]
    msg = frame_data["msg"]

    for p in points:
        if p in discarded:
            ax.scatter(p[0], p[1], color=DISCARDED_COLOR, s=20, zorder=1)
        else:
            ax.scatter(p[0], p[1], color=POINT_COLOR, s=30, zorder=2)

    for edge in final_edges:
        ax.plot(
            [edge[0][0], edge[1][0]],
            [edge[0][1], edge[1][1]],
            color=FINAL_COLOR,
            linewidth=2.5,
            zorder=3,
        )

    if active_line:
        ax.plot(
            [active_line[0][0], active_line[1][0]],
            [active_line[0][1], active_line[1][1]],
            color=HULL_COLOR,
            linewidth=2,
            linestyle="--",
            zorder=4,
        )

    if triangle:
        P, C, Q = triangle
        ax.plot(
            [P[0], C[0]], [P[1], C[1]], color=TRIANGLE_COLOR, linewidth=1.5, zorder=4
        )
        ax.plot(
            [C[0], Q[0]], [C[1], Q[1]], color=TRIANGLE_COLOR, linewidth=1.5, zorder=4
        )
        t_x, t_y = zip(P, C, Q)
        ax.fill(t_x, t_y, color=TRIANGLE_COLOR, alpha=0.15, zorder=1)

    if furthest:
        ax.scatter(
            furthest[0], furthest[1], color=ACTIVE_POINT, s=80, marker="*", zorder=6
        )
        if active_line and not triangle:
            cx = (active_line[0][0] + active_line[1][0]) / 2
            cy = (active_line[0][1] + active_line[1][1]) / 2
            ax.plot(
                [cx, furthest[0]],
                [cy, furthest[1]],
                color=ACTIVE_POINT,
                linestyle=":",
                alpha=0.6,
                zorder=3,
            )

    bbox_props = dict(
        boxstyle="round,pad=0.5", fc=BG_COLOR, ec=HULL_COLOR, lw=1, alpha=0.8
    )
    ax.text(
        np.mean(x),
        max(y) + 0.5,
        msg,
        color=TEXT_COLOR,
        fontsize=11,
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
