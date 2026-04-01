# convex-hull-visualizations

Visualizations of convex hull algorithms.

A visual exploration of 2D computational geometry algorithms. This project generates mathematical animations of 8 different convex hull algorithms to compare their operations and time complexities.

## Live demo

https://convex-hull-visualizations.vercel.app/

## Algorithms

- Brute force
- Jarvis March
- Monotone chain
- Graham Scan
- QuickHull
- Divide & Conquer (Merge hull)
- Kirkpatrick-Seidel
- Chan's Algorithm

## How to Run Locally

The project consists of two parts: the Python scripts that generate the animations, and the SvelteKit frontend that displays them.

### 1. Generating the Visualizations (Python)
The algorithms are written in Python and animated using Matplotlib.

```bash
cd convex-hull
pip install matplotlib numpy pillow
```

Run any of the algorithm scripts to generate a `.gif` file:
```bash
python3 chans_algorithm.py
```
*Note: Make sure to move the generated `.gif` files into the root `static/` directory before running the optimization script.*

### 2. Optimizing the Animations (Bash & FFmpeg)
Raw `.gif` files are too large for web hosting (some reaching 30MB+). The provided bash script converts them into highly compressed `.mp4` files using `ffmpeg`. 

Ensure you have `ffmpeg` installed on your system, then run:

```bash
./optimize_gifs.sh
```

**What this script does:**
* It scans the `static/` directory for `.gif` files.
* It converts standard algorithms to `.mp4` using a high-quality web profile.
* It applies an aggressive compression profile to the `brute_force` animations to drastically reduce their file size.
* The website frontend is configured to read the resulting `.mp4` files.

### 3. Running the Website (SvelteKit)
The frontend is built with SvelteKit, TailwindCSS, and KaTeX. Ensure you have Node.js installed.

Return to the root directory of the project:

```bash
# Install dependencies
npm install

# Start the local development server
npm run dev
```

Open `http://localhost:5173` in your browser to view the site.
