import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

NUM_POINTS = 40
GIF_FILENAME = "merge_hull.gif"
FPS = 4
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
DIM_HULL = "#2a4d5c"
HULL_COLOR = "#8be9fd"
FINAL_COLOR = "#50fa7b"
BRIDGE_COLOR = "#f1fa8c"
TEXT_COLOR = "#bd93f9"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def make_ccw(hull):
    cx = sum(p[0] for p in hull) / len(hull)
    cy = sum(p[1] for p in hull) / len(hull)
    return sorted(hull, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def base_case_hull(pts):
    pts = sorted(pts, key=lambda p: (p[0], p[1]))
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return make_ccw(lower[:-1] + upper[:-1])


def generate_frames(points):
    frames = []

    points = sorted(points, key=lambda p: p[0])
    chunks = [points[i : i + 5] for i in range(0, len(points), 5)]
    current_hulls = [base_case_hull(c) for c in chunks]

    frames.append(
        {
            "other": list(current_hulls),
            "L": [],
            "R": [],
            "bridge": None,
            "msg": "Base Cases Found",
        }
    )
    frames.append(
        {
            "other": list(current_hulls),
            "L": [],
            "R": [],
            "bridge": None,
            "msg": "Base Cases Found",
        }
    )

    while len(current_hulls) > 1:
        next_hulls = []
        for i in range(0, len(current_hulls), 2):
            if i + 1 < len(current_hulls):
                L = current_hulls[i]
                R = current_hulls[i + 1]

                other_hulls = [
                    current_hulls[j]
                    for j in range(len(current_hulls))
                    if j != i and j != i + 1
                ] + next_hulls

                ia = max(range(len(L)), key=lambda idx: L[idx][0])
                ib = min(range(len(R)), key=lambda idx: R[idx][0])

                frames.append(
                    {
                        "other": other_hulls,
                        "L": L,
                        "R": R,
                        "bridge": (L[ia], R[ib]),
                        "msg": "Starting Merge",
                    }
                )

                a, b = ia, ib
                while True:
                    changed = False
                    next_a = (a + 1) % len(L)
                    if cross_product(R[b], L[a], L[next_a]) < 0:
                        a = next_a
                        changed = True
                        frames.append(
                            {
                                "other": other_hulls,
                                "L": L,
                                "R": R,
                                "bridge": (L[a], R[b]),
                                "msg": "Walking Upper Bridge",
                            }
                        )
                        continue

                    next_b = (b - 1) % len(R)
                    if cross_product(L[a], R[b], R[next_b]) > 0:
                        b = next_b
                        changed = True
                        frames.append(
                            {
                                "other": other_hulls,
                                "L": L,
                                "R": R,
                                "bridge": (L[a], R[b]),
                                "msg": "Walking Upper Bridge",
                            }
                        )
                        continue

                    if not changed:
                        break

                upper_a, upper_b = a, b
                for _ in range(2):
                    frames.append(
                        {
                            "other": other_hulls,
                            "L": L,
                            "R": R,
                            "bridge": (L[upper_a], R[upper_b]),
                            "msg": "Upper Bridge Locked!",
                        }
                    )

                a, b = ia, ib
                frames.append(
                    {
                        "other": other_hulls,
                        "L": L,
                        "R": R,
                        "bridge": (L[a], R[b]),
                        "msg": "Finding Lower Bridge",
                    }
                )
                while True:
                    changed = False
                    next_a = (a - 1) % len(L)
                    if cross_product(R[b], L[a], L[next_a]) > 0:
                        a = next_a
                        changed = True
                        frames.append(
                            {
                                "other": other_hulls,
                                "L": L,
                                "R": R,
                                "bridge": (L[a], R[b]),
                                "msg": "Walking Lower Bridge",
                            }
                        )
                        continue

                    next_b = (b + 1) % len(R)
                    if cross_product(L[a], R[b], R[next_b]) < 0:
                        b = next_b
                        changed = True
                        frames.append(
                            {
                                "other": other_hulls,
                                "L": L,
                                "R": R,
                                "bridge": (L[a], R[b]),
                                "msg": "Walking Lower Bridge",
                            }
                        )
                        continue

                    if not changed:
                        break

                lower_a, lower_b = a, b
                for _ in range(2):
                    frames.append(
                        {
                            "other": other_hulls,
                            "L": L,
                            "R": R,
                            "bridge": (L[lower_a], R[lower_b]),
                            "msg": "Lower Bridge Locked!",
                        }
                    )

                merged = []
                curr = upper_a
                while True:
                    merged.append(L[curr])
                    if curr == lower_a:
                        break
                    curr = (curr + 1) % len(L)

                curr = lower_b
                while True:
                    merged.append(R[curr])
                    if curr == upper_b:
                        break
                    curr = (curr + 1) % len(R)

                next_hulls.append(merged)
                frames.append(
                    {
                        "other": other_hulls + [merged],
                        "L": [],
                        "R": [],
                        "bridge": None,
                        "msg": "Hulls Stitched!",
                    }
                )

            else:
                next_hulls.append(current_hulls[i])

        current_hulls = next_hulls

    final_hull = current_hulls[0]
    for _ in range(12):
        frames.append(
            {
                "other": [final_hull],
                "L": [],
                "R": [],
                "bridge": None,
                "msg": "Divide & Conquer Complete!",
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

    ax.scatter(*zip(*points), color=POINT_COLOR, s=30, zorder=1)

    other_hulls = frame_data["other"]
    L = frame_data["L"]
    R = frame_data["R"]
    bridge = frame_data["bridge"]
    msg = frame_data["msg"]

    def plot_poly(pts, color, style="-", alpha=1.0, lw=2.5):
        if len(pts) > 1:
            poly_pts = pts + [pts[0]]
            px, py = zip(*poly_pts)
            ax.plot(
                px,
                py,
                color=color,
                linewidth=lw,
                linestyle=style,
                alpha=alpha,
                zorder=3,
            )
            ax.fill(px, py, color=color, alpha=0.05 * alpha, zorder=1)

    is_done = msg == "Divide & Conquer Complete!"
    for h in other_hulls:
        plot_poly(
            h, FINAL_COLOR if is_done else DIM_HULL, alpha=1.0 if is_done else 0.5
        )

    if L:
        plot_poly(L, HULL_COLOR, lw=3)
    if R:
        plot_poly(R, HULL_COLOR, lw=3)

    if bridge:
        ax.plot(
            [bridge[0][0], bridge[1][0]],
            [bridge[0][1], bridge[1][1]],
            color=BRIDGE_COLOR,
            linestyle="--",
            linewidth=3.5,
            zorder=5,
        )
        ax.scatter(
            [bridge[0][0], bridge[1][0]],
            [bridge[0][1], bridge[1][1]],
            color=BRIDGE_COLOR,
            s=80,
            edgecolors="#121212",
            zorder=6,
        )

    bbox_props = dict(
        boxstyle="round,pad=0.5", fc=BG_COLOR, ec=HULL_COLOR, lw=1, alpha=0.9
    )
    if is_done:
        bbox_props["ec"] = FINAL_COLOR

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


print(f"Generating {len(frames)} frames at {FPS} FPS...")
ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=1000 / FPS, repeat=False
)

print(f"Saving to {GIF_FILENAME}...")
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done!")
