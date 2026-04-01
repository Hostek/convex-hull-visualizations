import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_POINTS = 40
GIF_FILENAME = "brute_force.gif"
FPS = 24
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
TEST_LINE_COLOR = "#f1fa8c"
CHECK_COLOR = "#8be9fd"
BAD_COLOR = "#ff5555"
FINAL_COLOR = "#50fa7b"
TEXT_COLOR = "#bd93f9"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def generate_frames(points):
    frames = []
    final_edges = []

    n = len(points)
    total_pairs = (n * (n - 1)) // 2
    pair_count = 0

    for i in range(n):
        for j in range(i + 1, n):
            pair_count += 1
            A, B = points[i], points[j]

            pos_count = 0
            neg_count = 0
            is_valid = True
            violator = None

            for k in range(n):
                if k == i or k == j:
                    continue

                C = points[k]

                frames.append(
                    {
                        "final": list(final_edges),
                        "testing": (A, B),
                        "checking": C,
                        "status": "eval",
                        "count": pair_count,
                        "total": total_pairs,
                    }
                )

                cp = cross_product(A, B, C)
                if cp > 0:
                    pos_count += 1
                elif cp < 0:
                    neg_count += 1

                if pos_count > 0 and neg_count > 0:
                    is_valid = False
                    violator = C
                    break

            if not is_valid:
                frames.append(
                    {
                        "final": list(final_edges),
                        "testing": (A, B),
                        "checking": violator,
                        "status": "fail",
                        "count": pair_count,
                        "total": total_pairs,
                    }
                )
            else:
                final_edges.append((A, B))
                for _ in range(15):
                    frames.append(
                        {
                            "final": list(final_edges),
                            "testing": (A, B),
                            "checking": None,
                            "status": "success",
                            "count": pair_count,
                            "total": total_pairs,
                        }
                    )

    for _ in range(40):
        frames.append(
            {
                "final": list(final_edges),
                "testing": None,
                "checking": None,
                "status": "done",
                "count": total_pairs,
                "total": total_pairs,
            }
        )

    return frames


np.random.seed(42)
angles = np.random.uniform(0, 2 * np.pi, NUM_POINTS)
radii = np.random.uniform(0, 10, NUM_POINTS)
x = radii * np.cos(angles)
y = radii * np.sin(angles)
points = list(zip(x, y))

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

    ax.scatter(*zip(*points), color=POINT_COLOR, s=30, zorder=1)

    final_edges = frame_data["final"]
    testing = frame_data["testing"]
    checking = frame_data["checking"]
    status = frame_data["status"]
    count = frame_data["count"]
    total = frame_data["total"]

    for edge in final_edges:
        ax.plot(
            [edge[0][0], edge[1][0]],
            [edge[0][1], edge[1][1]],
            color=FINAL_COLOR,
            linewidth=2.5,
            zorder=3,
        )

    if testing:
        A, B = testing

        if status == "eval":
            ax.plot(
                [A[0], B[0]], [A[1], B[1]], color=TEST_LINE_COLOR, linewidth=2, zorder=4
            )
            if checking:
                mid_x, mid_y = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
                ax.plot(
                    [mid_x, checking[0]],
                    [mid_y, checking[1]],
                    color=CHECK_COLOR,
                    linestyle=":",
                    linewidth=1.5,
                    zorder=2,
                )
                ax.scatter(checking[0], checking[1], color=CHECK_COLOR, s=50, zorder=5)

        elif status == "fail":
            ax.plot(
                [A[0], B[0]],
                [A[1], B[1]],
                color=BAD_COLOR,
                linewidth=2.5,
                linestyle="--",
                zorder=4,
            )
            if checking:
                ax.scatter(
                    checking[0],
                    checking[1],
                    color=BAD_COLOR,
                    s=100,
                    marker="x",
                    linewidths=2,
                    zorder=6,
                )

        elif status == "success":
            ax.plot(
                [A[0], B[0]], [A[1], B[1]], color=FINAL_COLOR, linewidth=4, zorder=5
            )

    msg = f"Brute Force O(N³)\nPairs Tested: {count} / {total}"
    if status == "done":
        msg = f"Brute Force Complete!\nTotal Tests: {total}"

    bbox_props = dict(
        boxstyle="round,pad=0.5",
        fc=BG_COLOR,
        ec=BAD_COLOR if status != "done" else FINAL_COLOR,
        lw=1.5,
        alpha=0.9,
    )
    ax.text(
        np.mean(x),
        max(y) + 0.5,
        msg,
        color=TEXT_COLOR,
        fontsize=12,
        ha="center",
        va="center",
        fontweight="bold",
        bbox=bbox_props,
        zorder=10,
    )


print("Running Brute Force algorithm (this generates A LOT of frames)...")
frames = generate_frames(points)
print(f"Generated {len(frames)} frames. Rendering GIF at {FPS} FPS...")

ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=1000 / FPS, repeat=False
)

print(f"Saving to {GIF_FILENAME}...")
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done!")
