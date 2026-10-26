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


def plot_daily_created_resolved(stats, output_path):
    """График №3: сверху задачи по дням, снизу накопительный итог."""
    if not stats.days:
        return False
    fig, (ax_day, ax_total) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax_day.plot(stats.days, stats.created, label="Создано", linewidth=0.7)
    ax_day.plot(stats.days, stats.resolved, label="Закрыто", linewidth=0.7)
    ax_day.set_ylabel("Задач за день")
    ax_day.set_title("Созданные и закрытые задачи по дням")
    ax_day.legend()

    ax_total.plot(stats.days, stats.created_cumulative, label="Создано (накопительно)")
    ax_total.plot(stats.days, stats.resolved_cumulative, label="Закрыто (накопительно)")
    ax_total.set_xlabel("Дата")
    ax_total.set_ylabel("Задач всего")
    ax_total.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return True


def plot_top_users(users, output_path):
    """График №4: горизонтальные столбики по пользователям,
    X — число задач, Y — имя пользователя."""
    if not users:
        return False
    height = 0.4
    positions = list(range(len(users)))
    fig, ax = plt.subplots(figsize=(10, 0.45 * len(users) + 2))
    ax.barh([p - height / 2 for p in positions],
            [u.assignee for u in users], height, label="Исполнитель")
    ax.barh([p + height / 2 for p in positions],
            [u.reporter for u in users], height, label="Репортер")
    ax.set_yticks(positions)
    ax.set_yticklabels([u.name for u in users])
    ax.invert_yaxis()  # самый активный пользователь сверху
    ax.set_xlabel("Количество задач")
    ax.set_ylabel("Пользователь")
    ax.set_title(f"Топ-{len(users)} пользователей по количеству задач")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return True


def plot_logged_time_histogram(hours, output_path, bins=50, project=""):
    """График №5: залогированное время по закрытым задачам."""
    suffix = f" ({project})" if project else ""
    return plot_duration_histogram(
        hours, output_path,
        title=f"Залогированное время по закрытым задачам{suffix}",
        xlabel="Залогированное время, часы",
        bins=bins,
    )