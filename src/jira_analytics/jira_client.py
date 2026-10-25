import logging
import time
import requests

log = logging.getLogger(__name__)

class JiraClientError(Exception):
    """Ошибка при обращении к JIRA REST API."""

class JiraClient:
    def __init__(self, base_url: str, page_size: int = 100,
                 retries: int = 3, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.page_size = page_size
        self.retries = retries
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}{path}"
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                log.warning("Запрос %s не удался (попытка %d/%d): %s",
                            url, attempt, self.retries, exc)
                if attempt == self.retries:
                    raise JiraClientError(f"Не удалось получить {url}") from exc
                time.sleep(2 ** attempt)

    def search_issues(self, jql: str, fields: list[str]):
        """Генератор задач по JQL с постраничной загрузкой."""
        start = 0
        while True:
            data = self._get("/rest/api/2/search", {
                "jql": jql, "fields": ",".join(fields),
                "startAt": start, "maxResults": self.page_size,
            })
            issues = data["issues"]
            if not issues:
                return
            yield from issues
            start += len(issues)
            log.info("Загружено %d из %d", start, data["total"])
            if start >= data["total"]:
                return