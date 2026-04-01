import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_POINTS = 40
GIF_FILENAME = "chans_algorithm.gif"
FPS = 3
DPI = 120

BG_COLOR = "#121212"
POINT_COLOR = "#555555"
GLOBAL_HULL = "#ffffff"
LASER_COLOR = "#ff79c6"
BEST_COLOR = "#f1fa8c"
FAIL_COLOR = "#ff5555"
SUCCESS_COLOR = "#50fa7b"

PALETTE = [
    "#8be9fd",
    "#bd93f9",
    "#ffb86c",
    "#ff79c6",
    "#f1fa8c",
    "#8ae234",
    "#fcaf3e",
    "#ad7fa8",
]


def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def dist(p0, p1):
    return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2


def base_case_hull(pts):
    if len(pts) <= 2:
        return pts
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
    return lower[:-1] + upper[:-1]


def get_tangent(p_curr, mh):
    best_p = mh[0]
    if best_p == p_curr and len(mh) > 1:
        best_p = mh[1]
    for p in mh:
        if p == p_curr:
            continue
        cp = cross_product(p_curr, best_p, p)
        if cp < 0 or (cp == 0 and dist(p_curr, p) > dist(p_curr, best_p)):
            best_p = p
    return best_p


def generate_frames(points):
    frames = []
    n = len(points)

    points = sorted(points, key=lambda p: p[0])
    p_start = min(points, key=lambda p: (p[1], p[0]))

    t = 1
    while True:
        m = min(n, 2 ** (2**t))

        chunks = [points[i : i + m] for i in range(0, n, m)]
        mini_hulls = [base_case_hull(c) for c in chunks]

        for _ in range(6):
            frames.append(
                {
                    "mh": mini_hulls,
                    "gh": [],
                    "laser": None,
                    "best": None,
                    "status": "info",
                    "msg": f"Phase {t}: Guessing Hull Size m = {m}\nDividing points into groups of {m}",
                }
            )

        p_curr = p_start
        global_hull = [p_curr]
        success = False

        for step in range(1, m + 1):
            best_overall = None

            for idx, mh in enumerate(mini_hulls):
                best_tangent = get_tangent(p_curr, mh)

                best_line = (p_curr, best_overall) if best_overall is not None else None

                frames.append(
                    {
                        "mh": mini_hulls,
                        "gh": list(global_hull),
                        "laser": (p_curr, best_tangent),
                        "best": best_line,
                        "active_idx": idx,
                        "status": "eval",
                        "msg": f"Step {step} of {m}\nFinding tangent for Group {idx+1}...",
                    }
                )

                if best_overall is None:
                    best_overall = best_tangent
                else:
                    cp = cross_product(p_curr, best_overall, best_tangent)
                    if cp < 0 or (
                        cp == 0
                        and dist(p_curr, best_tangent) > dist(p_curr, best_overall)
                    ):
                        best_overall = best_tangent

            for _ in range(2):
                frames.append(
                    {
                        "mh": mini_hulls,
                        "gh": list(global_hull),
                        "laser": None,
                        "best": (p_curr, best_overall),
                        "active_idx": -1,
                        "status": "locked",
                        "msg": f"Step {step} of {m}\nLocking best overall tangent!",
                    }
                )

            global_hull.append(best_overall)
            p_curr = best_overall

            if p_curr == p_start:
                success = True
                break

        if success:
            for _ in range(15):
                frames.append(
                    {
                        "mh": mini_hulls,
                        "gh": list(global_hull),
                        "laser": None,
                        "best": None,
                        "active_idx": -1,
                        "status": "success",
                        "msg": f"SUCCESS!\nHull closed in {step} steps.\n({step} <= {m})",
                    }
                )
            break
        else:
            for _ in range(8):
                frames.append(
                    {
                        "mh": mini_hulls,
                        "gh": list(global_hull),
                        "laser": None,
                        "best": None,
                        "active_idx": -1,
                        "status": "fail",
                        "msg": f"ABORT!\nReached limit of {m} steps but didn't close loop.\nm was too small. Squaring m!",
                    }
                )
            t += 1

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

    mh = frame_data["mh"]
    gh = frame_data["gh"]
    laser = frame_data["laser"]
    best = frame_data["best"]
    active_idx = frame_data.get("active_idx", -1)
    status = frame_data["status"]
    msg = frame_data["msg"]

    ax.scatter(*zip(*points), color=POINT_COLOR, s=30, zorder=1)

    for idx, h in enumerate(mh):
        color = PALETTE[idx % len(PALETTE)]
        alpha = 0.9 if idx == active_idx else 0.3
        linewidth = 2.5 if idx == active_idx else 1.0

        if status == "success":
            alpha = 0.1
            linewidth = 0.5

        if len(h) > 1:
            poly = h + [h[0]]
            px, py = zip(*poly)
            ax.plot(px, py, color=color, linewidth=linewidth, alpha=alpha, zorder=2)
            ax.fill(px, py, color=color, alpha=alpha * 0.15, zorder=1)

    gh_color = (
        FAIL_COLOR
        if status == "fail"
        else (SUCCESS_COLOR if status == "success" else GLOBAL_HULL)
    )
    if len(gh) > 1:
        px, py = zip(*gh)
        ax.plot(px, py, color=gh_color, linewidth=3.5, zorder=4)
        ax.scatter(px, py, color=gh_color, s=50, zorder=5)

    if laser:
        color = PALETTE[active_idx % len(PALETTE)]
        ax.plot(
            [laser[0][0], laser[1][0]],
            [laser[0][1], laser[1][1]],
            color=color,
            linestyle=":",
            linewidth=2,
            zorder=6,
        )
        ax.scatter(laser[1][0], laser[1][1], color=color, s=80, marker="+", zorder=7)

    if best:
        ax.plot(
            [best[0][0], best[1][0]],
            [best[0][1], best[1][1]],
            color=BEST_COLOR,
            linestyle="--",
            linewidth=2.5,
            zorder=5,
        )
        ax.scatter(best[1][0], best[1][1], color=BEST_COLOR, s=60, zorder=6)

    bbox_props = dict(
        boxstyle="round,pad=0.6", fc=BG_COLOR, ec=GLOBAL_HULL, lw=1.5, alpha=0.9
    )
    if status == "fail":
        bbox_props["ec"] = FAIL_COLOR
    elif status == "success":
        bbox_props["ec"] = SUCCESS_COLOR
    elif active_idx >= 0:
        bbox_props["ec"] = PALETTE[active_idx % len(PALETTE)]

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


print("Running Fixed Chan's Algorithm...")
frames = generate_frames(points)
print(f"Generated {len(frames)} frames. Rendering GIF at {FPS} FPS...")

ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=1000 / FPS, repeat=False
)
ani.save(GIF_FILENAME, dpi=DPI, writer=animation.PillowWriter(fps=FPS))
print("Done!")
