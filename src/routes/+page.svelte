<script lang="ts">
    import katex from "katex"
    import "katex/dist/katex.min.css"

    function math(tex: string): string {
        return katex.renderToString(tex, {
            throwOnError: false,
            displayMode: false,
        })
    }

    function playWhenVisible(node: HTMLVideoElement) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        node.play().catch(() => {})
                    } else {
                        node.pause()
                    }
                })
            },
            { threshold: 0.1 },
        )

        observer.observe(node)

        return {
            destroy() {
                observer.disconnect()
            },
        }
    }

    const algorithms = [
        {
            id: "brute-force",
            name: "Brute Force",
            time: "O(n^3)",
            space: "O(1)",
            video: "/brute_force.mp4",
            desc: "The absolute baseline. It checks every possible line segment against every other point. An incredibly inefficient but highly educational visualization.",
        },
        {
            id: "jarvis-march",
            name: "Jarvis March (Gift Wrapping)",
            time: "O(n \\cdot h)",
            space: "O(1)",
            video: "/jarvis_march.mp4",
            desc: 'An output-sensitive algorithm. It sweeps a laser to find the widest right-turn, effectively "wrapping" a string around the outside of the points. Very fast if the hull has few points (small h).',
        },
        {
            id: "monotone-chain",
            name: "Monotone Chain",
            time: "O(n \\log n)",
            space: "O(n)",
            video: "/monotone_chain.mp4",
            desc: "The undisputed king of Competitive Programming. It sorts points by X-coordinate, then builds the lower and upper bounds left-to-right. Extremely robust because it completely avoids complex floating-point polar angles.",
        },
        {
            id: "graham-scan",
            name: "Graham Scan",
            time: "O(n \\log n)",
            space: "O(n)",
            video: "/graham_scan.mp4",
            desc: "The classic algorithm. It finds the lowest point, sorts all other points by their polar angle (like a sweeping radar), and maintains a stack to prune concave turns.",
        },
        {
            id: "quickhull",
            name: "QuickHull",
            time: "O(n \\log n) \\text{ avg}",
            space: "O(n)",
            video: "/quick_hull.mp4",
            desc: "Similar to QuickSort. It draws a baseline, finds the furthest point to form a triangle, and ruthlessly deletes all points trapped inside. Extremely fast in practice.",
        },
        {
            id: "merge-hull",
            name: "Divide & Conquer",
            time: "O(n \\log n)",
            space: "O(n)",
            video: "/merge_hull.mp4",
            desc: '"Conquest before Marriage". It divides the points into tiny sub-hulls, solves them, and then uses walking tangent threads to perfectly stitch them together.',
        },
        {
            id: "kirkpatrick-seidel",
            name: "Kirkpatrick-Seidel",
            time: "O(n \\log h)",
            space: "O(n)",
            video: "/kirkpatrick_seidel.mp4",
            desc: '"Marriage before Conquest". It mathematically predicts the bridging upper tangent before recursing, allowing it to instantly delete massive chunks of points trapped underneath.',
        },
        {
            id: "chans-algo",
            name: "Chan's Algorithm",
            time: "O(n \\log h)",
            space: "O(n)",
            video: "/chans_algorithm.mp4",
            desc: "The Holy Grail. The absolute theoretical limit of 2D geometry. It duct-tapes Graham Scan and Jarvis March together, guessing the hull size and dynamically resizing until it snaps perfectly into place.",
        },
    ]
</script>

<svelte:head>
    <title>Convex Hull Visualizations</title>
    <meta name="description" content="Visualizing 2D Convex Hull Algorithms" />
</svelte:head>

<main class="mx-auto max-w-4xl px-6 py-16">
    <!-- Hero Section -->
    <div class="prose prose-invert prose-zinc max-w-none mb-16">
        <h1
            class="bg-linear-to-r from-cyan-400 to-green-400 bg-clip-text text-transparent mb-4 text-5xl font-extrabold"
        >
            Convex Hull Algorithms
        </h1>
        <p class="text-xl text-zinc-400 leading-relaxed">
            A visual exploration of computational geometry. How do different
            algorithms think about the exact same set of points? Watch them
            visually construct the optimal outer boundary.
        </p>
    </div>

    <section class="mb-20">
        <div class="prose prose-invert prose-zinc max-w-none mb-6">
            <h2>Time & Space Complexity</h2>
        </div>
        <div
            class="overflow-x-auto rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm"
        >
            <table
                class="w-full text-left text-sm text-zinc-300 whitespace-nowrap"
            >
                <thead class="bg-zinc-800/50 text-xs uppercase text-zinc-400">
                    <tr>
                        <th class="px-6 py-4 font-semibold tracking-wider"
                            >Algorithm</th
                        >
                        <th class="px-6 py-4 font-semibold tracking-wider"
                            >Time Complexity</th
                        >
                        <th class="px-6 py-4 font-semibold tracking-wider"
                            >Space Complexity</th
                        >
                    </tr>
                </thead>
                <tbody class="divide-y divide-zinc-800/50">
                    {#each algorithms as algo (algo.id)}
                        <tr class="hover:bg-zinc-800/30 transition-colors">
                            <td class="px-6 py-4 font-medium text-white"
                                >{algo.name}</td
                            >
                            <td class="px-6 py-4">{@html math(algo.time)}</td>
                            <td class="px-6 py-4 text-zinc-500"
                                >{@html math(algo.space)}</td
                            >
                        </tr>
                    {/each}
                </tbody>
            </table>
            <div class="p-4 text-xs text-zinc-500 italic bg-zinc-950/50">
                * Where <span class="font-semibold text-zinc-300">n</span> is
                the total number of points, and
                <span class="font-semibold text-zinc-300">h</span> is the number
                of points that end up on the final hull.
            </div>
        </div>
    </section>

    <div class="space-y-24">
        {#each algorithms as algo (algo.id)}
            <section id={algo.id} class="group scroll-mt-8">
                <div class="prose prose-invert prose-zinc max-w-none mb-6">
                    <div class="flex items-center gap-4">
                        <h2 class="m-0 text-3xl font-bold">{algo.name}</h2>
                        <span
                            class="rounded-full bg-zinc-800 px-3 py-1 text-sm font-medium text-cyan-300 border border-zinc-700"
                        >
                            {@html math(algo.time)}
                        </span>
                    </div>
                    <p class="text-zinc-400 mt-3 text-lg leading-relaxed">
                        {algo.desc}
                    </p>
                </div>

                <div
                    class="relative overflow-hidden rounded-2xl border border-zinc-800 bg-[#121212] shadow-2xl transition-all duration-500 group-hover:border-zinc-600 group-hover:shadow-cyan-900/10"
                >
                    <video
                        use:playWhenVisible
                        src={algo.video}
                        muted
                        loop
                        playsinline
                        preload="metadata"
                        class="w-full object-cover"
                        style="aspect-ratio: 1 / 1;"
                    ></video>
                </div>
            </section>
        {/each}
    </div>
</main>
