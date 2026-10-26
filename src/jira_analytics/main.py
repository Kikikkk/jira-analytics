import argparse
import logging
import sys

from .analytics import (
    daily_created_resolved,
    open_durations_days,
    time_in_status_days,
    top_users,
)
from .config import ConfigError, load_config
from .issue_mapper import to_issue
from .jira_client import JiraClient, JiraClientError
from .plots import (
    plot_daily_created_resolved,
    plot_open_time_histogram,
    plot_status_time_histograms,
    plot_top_users,
)

log = logging.getLogger(__name__)

FIELDS = ["created", "resolutiondate", "status"]
FIELDS_LIGHT = ["created", "resolutiondate", "assignee", "reporter"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Аналитика задач JIRA")
    parser.add_argument("--config", default="config.ini", help="путь к config.ini")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_args()
    try:
        cfg = load_config(args.config)
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        client = JiraClient(cfg.base_url, cfg.page_size, cfg.retries, cfg.timeout)

        # Закрытые задачи с историей: графики №1 и №2
        closed_jql = f"project = {cfg.project} AND resolution IS NOT EMPTY ORDER BY created ASC"
        closed = [
            to_issue(raw)
            for raw in client.search_issues(closed_jql, FIELDS, expand="changelog")
        ]
        log.info("Закрытых задач: %d", len(closed))

        plot_open_time_histogram(
            open_durations_days(closed),
            cfg.output_dir / "01_open_time_histogram.png",
            bins=cfg.bins,
            max_days=cfg.max_days,
        )

        by_status = time_in_status_days(closed)
        for status, values in sorted(by_status.items()):
            log.info("Статус %s: значений %d", status, len(values))
        paths = plot_status_time_histograms(
            by_status, cfg.output_dir, bins=cfg.bins, max_days=cfg.max_days
        )
        log.info("Построено графиков по статусам: %d", len(paths))

        # Все задачи, без changelog: график №3
        all_jql = f"project = {cfg.project} ORDER BY created ASC"
        all_issues = [
            to_issue(raw)
            for raw in client.search_issues(all_jql, FIELDS_LIGHT)
        ]
        stats = daily_created_resolved(all_issues)
        if stats.days:
            log.info("Всего задач: %d, закрытых: %d",
                     stats.created_cumulative[-1], stats.resolved_cumulative[-1])
        plot_daily_created_resolved(
            stats, cfg.output_dir / "03_created_vs_resolved.png"
        )
        
        # График №4: те же задачи, что и для графика №3
        unassigned = sum(1 for i in all_issues if i.assignee is None)
        log.info("Задач без исполнителя: %d", unassigned)
        users = top_users(all_issues, cfg.top_users)
        for user in users[:3]:
            log.info("%s: исполнитель %d, репортер %d",
                     user.name, user.assignee, user.reporter)
        plot_top_users(users, cfg.output_dir / "04_top_users.png")
        return 0
    except (ConfigError, JiraClientError) as exc:
        log.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())