import matplotlib.pyplot as plt

def plot_open_time_histogram(durations_days, output_path, bins=50, max_days=None):
    """Гистограмма: X — дни в открытом состоянии, Y — число задач."""
    data = [d for d in durations_days if max_days is None or d <= max_days]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=bins, edgecolor="black")
    ax.set_xlabel("Время в открытом состоянии, дни")
    ax.set_ylabel("Количество задач")
    ax.set_title("Распределение времени жизни закрытых задач")
    ax.set_yscale("log")   # хвост очень длинный, иначе видно один столбик
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)