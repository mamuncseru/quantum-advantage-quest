"""Render the DQI-vs-Prange advantage window figure (light + dark SVG).

Run from repo root: .venv/bin/python hunt/code/window_figure.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from advantage_window import window  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INK = {
    "light": dict(secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", axis="#c3c2b7"),
    "dark": dict(secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", axis="#383835"),
}
SERIES = {"light": ["#2a78d6", "#1baf7a", "#eda100"],
          "dark": ["#3987e5", "#199e70", "#c98500"]}

x = np.linspace(0.001, 0.999, 999)
mus = (0.5, 0.3, 0.7)

for mode in ("light", "dark"):
    ink, c = INK[mode], SERIES[mode]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(ink["axis"])
    ax.tick_params(colors=ink["muted"], labelsize=9)
    ax.grid(True, color=ink["grid"], linewidth=0.6)
    ax.set_axisbelow(True)
    for i, mu in enumerate(mus):
        g = window(x, mu)
        ax.plot(x, g, color=c[i], lw=2, zorder=3)
        j = int(np.argmax(g))
        label = f"r/p = {mu}" + ("  (paper's slice)" if mu == 0.5 else "")
        ax.annotate(label, (x[j], g[j]), xytext=(x[j] - 0.06, g[j] + 0.012),
                    color=ink["secondary"], fontsize=9)
    ax.axhline(0, color=ink["muted"], lw=1, ls=(0, (4, 3)))
    ax.set_xlabel("n/p   (degree bound / field size)")
    ax.set_ylabel("DQI − Prange   (satisfied fraction)")
    ax.set_title("The OPI advantage window from the verified semicircle law "
                 "(arXiv 2408.08292v5, Eq. 6)", fontsize=10,
                 color=ink["secondary"])
    for lbl in (ax.xaxis.label, ax.yaxis.label):
        lbl.set_color(ink["secondary"])
        lbl.set_fontsize(10)
    suffix = "-dark" if mode == "dark" else ""
    out = ROOT / f"fig-window{suffix}.svg"
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(out)
