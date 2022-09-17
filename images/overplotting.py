import matplotlib.pyplot as plt
import numpy as np


with plt.xkcd():
    rng = np.random.default_rng(30941)

    fig, axes = plt.subplots(nrows=3, figsize=(12, 4))
    for ax, n in zip(axes, [100, 1000, 10000]):
        x = np.linspace(0.0, 1.0, n)
        y = rng.standard_normal(n)

        ax.plot(x, y)
        ax.set_title(f"Line with {n} points")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    fig.savefig("overplotting.png")
