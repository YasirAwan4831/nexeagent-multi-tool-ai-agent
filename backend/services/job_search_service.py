"""Job search via Remotive API + keyword filtering."""

from __future__ import annotations

import re
from urllib.parse import quote_plus

import requests

from config import JOBS_FILE
from services.gemini_service import gemini_service
from utils.helpers import extract_company_from_title, generate_id, utc_now_iso
from utils.json_db import JsonDatabase
from utils.logger import log_event

DEFAULT_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "automation",
    "python",
    "flask",
    "react",
    "full stack",
    "fullstack",
    "remote",
    "web development",
    "developer",
    "machine learning",
    "llm",
]

REMOTIVE_API = "https://remotive.com/api/remote-jobs"


class JobSearchService:
    def __init__(self):
        self.db = JsonDatabase(JOBS_FILE, default=[])

    def search_jobs(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Fetch remote jobs and filter by query/keywords."""
        try:
            params = {}
            if category:
                params["category"] = category
            response = requests.get(REMOTIVE_API, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            jobs_raw = data.get("jobs", [])
        except Exception as exc:
            log_event("error", f"Job API error: {exc}")
            return self._fallback_search(query or "developer", limit)

        keywords = self._build_keywords(query)
        results = []

        for job in jobs_raw:
            searchable = " ".join(
                [
                    str(job.get("title", "")),
                    str(job.get("company_name", "")),
                    str(job.get("category", "")),
                    str(job.get("job_type", "")),
                    " ".join(job.get("tags", []) or []),
                    str(job.get("description", ""))[:500],
                ]
            ).lower()

            if keywords and not any(kw in searchable for kw in keywords):
                continue

            company = job.get("company_name") or extract_company_from_title(
                job.get("title", "")
            )
            entry = {
                "id": generate_id("job"),
                "title": job.get("title", "Untitled"),
                "company": company,
                "url": job.get("url", ""),
                "location": job.get("candidate_required_location", "Remote"),
                "category": job.get("category", ""),
                "job_type": job.get("job_type", ""),
                "publication_date": job.get("publication_date", ""),
                "description": (job.get("description") or "")[:400],
                "tags": job.get("tags", []) or [],
                "source": "remotive",
                "searched_at": utc_now_iso(),
                "query": query or "default",
            }
            results.append(entry)
            if len(results) >= limit:
                break

        if results:
            self._persist_jobs(results)

        return results

    def _build_keywords(self, query: str | None) -> list[str]:
        if not query or not query.strip():
            return [k.lower() for k in DEFAULT_KEYWORDS]
        parts = re.split(r"[,;\s]+", query.lower())
        keywords = [p for p in parts if p and len(p) > 1]
        return keywords or [k.lower() for k in DEFAULT_KEYWORDS]

    def _fallback_search(self, query: str, limit: int) -> list[dict]:
        """Generate placeholder results when API fails (demo mode)."""
        log_event("warning", "Using fallback job data")
        q = quote_plus(query)
        return [
            {
                "id": generate_id("job"),
                "title": f"{query.title()} Developer (Sample)",
                "company": "Tech Company",
                "url": f"https://www.google.com/search?q={q}+jobs",
                "location": "Remote",
                "category": "software-dev",
                "description": f"Sample listing — configure network access. Search: {query}",
                "source": "fallback",
                "searched_at": utc_now_iso(),
                "query": query,
            }
        ][:limit]

    def _persist_jobs(self, jobs: list[dict]) -> None:
        stored = self.db.read()
        existing_urls = {j.get("url") for j in stored}
        for job in jobs:
            if job.get("url") not in existing_urls:
                stored.append(job)
        self.db.write(stored[-200:])

    def list_saved_jobs(
        self,
        query: str | None = None,
        company: str | None = None,
    ) -> list[dict]:
        jobs = self.db.read()
        if query:
            q = query.lower()
            jobs = [
                j
                for j in jobs
                if q in (j.get("title", "") + j.get("description", "")).lower()
            ]
        if company:
            c = company.lower()
            jobs = [j for j in jobs if c in j.get("company", "").lower()]
        return sorted(jobs, key=lambda x: x.get("searched_at", ""), reverse=True)

    def summarize_jobs(self, jobs: list[dict]) -> str:
        if not jobs:
            return "No jobs found matching your criteria."
        lines = []
        for i, job in enumerate(jobs[:10], 1):
            lines.append(
                f"{i}. {job.get('title')} @ {job.get('company')} — {job.get('url')}"
            )
        text = "\n".join(lines)
        if gemini_service.is_available:
            return gemini_service.summarize(
                f"Summarize these job listings for a developer:\n{text}"
            )
        return text


job_search_service = JobSearchService()
