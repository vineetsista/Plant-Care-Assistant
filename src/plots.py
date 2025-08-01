import matplotlib.pyplot as plt
from dataset import load_plants


def plot_category_counts():
    df = load_plants()
    counts = df["category"].value_counts()
    fig, ax = plt.subplots()
    counts.plot.bar(ax=ax)
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Plants")
    ax.set_title("Plant Category Distribution")
    plt.tight_layout()
    return fig
