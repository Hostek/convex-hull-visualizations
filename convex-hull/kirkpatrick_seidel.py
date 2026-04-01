import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_POINTS = 40
GIF_FILENAME = "kirkpatrick_seidel.gif"
FPS = 3
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
ACTIVE_PT = "#ffffff"
DISCARDED = "#222222"
FINAL_EDGE = "#50fa7b"
BRIDGE_COLOR = "#f1fa8c"
SPLIT_COLOR = "#ff79c6"
BURN_COLOR = "#ff5555"


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def get_upper_bridge(S, x_med):
    """Finds the upper bridge crossing x_med perfectly using L-to-R sweep."""
    pts = sorted(S, key=lambda p: (p[0], p[1]))
    upper = []
    for p in pts:
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) >= 0:
            upper.pop()
        upper.append(p)
    for i in range(len(upper) - 1):
        if upper[i][0] < x_med < upper[i + 1][0]:
            return upper[i], upper[i + 1]
    return None, None


def get_lower_bridge(S, x_med):
    """Finds the lower bridge crossing x_med perfectly using L-to-R sweep."""
    pts = sorted(S, key=lambda p: (p[0], p[1]))
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for i in range(len(lower) - 1):
        if lower[i][0] < x_med < lower[i + 1][0]:
            return lower[i], lower[i + 1]
    return None, None


def generate_frames(points):
    frames = []
    final_edges = []
    discarded_set = set()

    def add_frame(active, split, bridge, burning, msg, pause=1):
        for _ in range(pause):
            frames.append(
                {
                    "edges": list(final_edges),
                    "discarded": set(discarded_set),
                    "active": list(active),
                    "split": split,
                    "bridge": bridge,
                    "burning": list(burning),
                    "msg": msg,
                }
            )

    def ks_upper(S):
        unique_x = sorted(list(set(p[0] for p in S)))
        if len(unique_x) < 2:
            return

        mid = len(unique_x) // 2
        x_med = (unique_x[mid - 1] + unique_x[mid]) / 2.0

        add_frame(S, x_med, None, [], "Upper Hull: Splitting set by Median X", 2)

        pl, pr = get_upper_bridge(S, x_med)
        if not pl or not pr:
            return

        add_frame(
            S,
            x_med,
            (pl, pr),
            [],
            "Marriage: Finding Upper Bridge BEFORE recursing!",
            2,
        )
        final_edges.append((pl, pr))

        S_left = [p for p in S if p[0] <= pl[0]]
        S_right = [p for p in S if p[0] >= pr[0]]
        discard_now = [p for p in S if p not in S_left and p not in S_right]

        if discard_now:
            add_frame(
                S,
                x_med,
                (pl, pr),
                discard_now,
                "Prune: Points under the bridge are instantly discarded!",
                2,
            )
            for p in discard_now:
                discarded_set.add(p)

        ks_upper(S_left)
        ks_upper(S_right)

    def ks_lower(S):
        unique_x = sorted(list(set(p[0] for p in S)))
        if len(unique_x) < 2:
            return

        mid = len(unique_x) // 2
        x_med = (unique_x[mid - 1] + unique_x[mid]) / 2.0

        add_frame(S, x_med, None, [], "Lower Hull: Splitting set by Median X", 2)

        pl, pr = get_lower_bridge(S, x_med)
        if not pl or not pr:
            return

        add_frame(
            S,
            x_med,
            (pl, pr),
            [],
            "Marriage: Finding Lower Bridge BEFORE recursing!",
            2,
        )
        final_edges.append((pl, pr))

        S_left = [p for p in S if p[0] <= pl[0]]
        S_right = [p for p in S if p[0] >= pr[0]]
        discard_now = [p for p in S if p not in S_left and p not in S_right]

        if discard_now:
            add_frame(
                S,
                x_med,
                (pl, pr),
                discard_now,
                "Prune: Points above the lower bridge are instantly discarded!",
                2,
            )
            for p in discard_now:
                discarded_set.add(p)

        ks_lower(S_left)
        ks_lower(S_right)

    add_frame(
        points, None, None, [], "Kirkpatrick-Seidel Algorithm\nPhase 1: Upper Hull", 3
    )
    ks_upper(points)

    add_frame(points, None, None, [], "Upper Hull Complete!\nPhase 2: Lower Hull", 3)
    ks_lower(points)

    add_frame(
        [],
        None,
        None,
        [],
        "Kirkpatrick-Seidel Complete!\nThe 'Ultimate' O(N log h) Algorithm",
        12,
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

    edges = frame_data["edges"]
    discarded = frame_data["discarded"]
    active = frame_data["active"]
    split = frame_data["split"]
    bridge = frame_data["bridge"]
    burning = frame_data["burning"]
    msg = frame_data["msg"]

    for p in points:
        if p in burning:
            ax.scatter(
                p[0],
                p[1],
                color=BURN_COLOR,
                s=120,
                marker="x",
                linewidths=2.5,
                zorder=6,
            )
        elif p in discarded:
            ax.scatter(p[0], p[1], color=DISCARDED, s=20, zorder=1)
        elif p in active:
            ax.scatter(p[0], p[1], color=ACTIVE_PT, s=45, zorder=3)
        else:
            ax.scatter(p[0], p[1], color=POINT_COLOR, s=20, alpha=0.4, zorder=2)

    for edge in edges:
        ax.plot(
            [edge[0][0], edge[1][0]],
            [edge[0][1], edge[1][1]],
            color=FINAL_EDGE,
            linewidth=3,
            zorder=4,
        )

    if split is not None:
        ax.axvline(x=split, color=SPLIT_COLOR, linestyle=":", linewidth=2, zorder=2)

    if bridge:
        ax.plot(
            [bridge[0][0], bridge[1][0]],
            [bridge[0][1], bridge[1][1]],
            color=BRIDGE_COLOR,
            linestyle="--",
            linewidth=4,
            zorder=5,
        )
        ax.scatter(
            [bridge[0][0], bridge[1][0]],
            [bridge[0][1], bridge[1][1]],
            color=BRIDGE_COLOR,
            s=80,
            zorder=6,
        )

    bbox_props = dict(
        boxstyle="round,pad=0.6", fc=BG_COLOR, ec=ACTIVE_PT, lw=1.5, alpha=0.9
    )
    if "Complete" in msg:
        bbox_props["ec"] = FINAL_EDGE
    elif "Marriage" in msg:
        bbox_props["ec"] = BRIDGE_COLOR
    elif "Prune" in msg:
        bbox_props["ec"] = BURN_COLOR
    elif "Divide" in msg or "Split" in msg:
        bbox_props["ec"] = SPLIT_COLOR

    ax.text(
        np.mean(x),
        max(y) + 0.5,
        msg,
        color="#ffffff",
        fontsize=12,
        ha="center",
        va="center",
        fontweight="bold",
        bbox=bbox_props,
        zorder=10,
    )


print("Running Kirkpatrick-Seidel (Fixed Correctness & Pacing)...")
frames = generate_frames(points)
print(f"Generated {len(frames)} frames. Rendering GIF at {FPS} FPS...")

ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=1000 / FPS, repeat=False
)
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done! You now have a flawless 'Marriage Before Conquest' visual.")
