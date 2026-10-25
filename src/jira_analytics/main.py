import argparse
import logging
import sys

from .analytics import open_durations_days, parse_jira_datetime
from .config import ConfigError, load_config
from .jira_client import JiraClient, JiraClientError
from .models import Issue
from .plots import plot_open_time_histogram

log = logging.getLogger(__name__)

FIELDS = ["created", "resolutiondate", "status"]


def to_issue(raw: dict) -> Issue:
    """Преобразует JSON задачи из JIRA в модель Issue."""
    fields = raw["fields"]
    return Issue(
        key=raw["key"],
        created=parse_jira_datetime(fields["created"]),
        resolved=parse_jira_datetime(fields.get("resolutiondate")),
    )


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
        jql = f"project = {cfg.project} AND resolution IS NOT EMPTY ORDER BY created ASC"
        issues = [to_issue(raw) for raw in client.search_issues(jql, FIELDS)]
        log.info("Закрытых задач: %d", len(issues))

        durations = open_durations_days(issues)
        plot_open_time_histogram(
            durations,
            cfg.output_dir / "01_open_time_histogram.png",
            bins=cfg.bins,
            max_days=cfg.max_days,
        )
        log.info("График сохранён в %s", cfg.output_dir)
        return 0
    except (ConfigError, JiraClientError) as exc:
        log.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())