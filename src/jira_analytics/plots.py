import re
from pathlib import Path

import matplotlib.pyplot as plt


def plot_duration_histogram(durations_days, output_path, title,
                            xlabel="Время, дни", bins=50, max_days=None):
    """Гистограмма длительностей: X — дни, Y — число задач (лог. шкала)."""
    data = [d for d in durations_days if max_days is None or d <= max_days]
    if not data:
        return False
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=bins, edgecolor="black")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Количество задач")
    ax.set_title(title)
    ax.set_yscale("log")
    ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return True


def plot_open_time_histogram(durations_days, output_path, bins=50, max_days=None):
    """График №1: время жизни закрытых задач."""
    plot_duration_histogram(
        durations_days, output_path,
        title="Распределение времени жизни закрытых задач",
        xlabel="Время в открытом состоянии, дни",
        bins=bins, max_days=max_days,
    )


def status_to_filename(status: str) -> str:
    """'Patch Available' -> 'patch_available' (безопасное имя файла)."""
    return re.sub(r"[^a-z0-9]+", "_", status.lower()).strip("_") or "unknown"


def plot_status_time_histograms(durations_by_status, output_dir: Path,
                                bins=50, max_days=None) -> list[Path]:
    """График №2: отдельная гистограмма для каждого статуса."""
    paths = []
    for status, durations in sorted(durations_by_status.items()):
        path = output_dir / f"02_status_{status_to_filename(status)}.png"
        if plot_duration_histogram(
            durations, path,
            title=f"Время в статусе «{status}»",
            xlabel=f"Время в статусе «{status}», дни",
            bins=bins, max_days=max_days,
        ):
            paths.append(path)
    return paths