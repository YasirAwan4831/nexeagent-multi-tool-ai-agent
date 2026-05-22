"""Web/job search tool wrapper for agent execution."""

from services.job_search_service import job_search_service


def search_jobs(query: str, limit: int = 10) -> dict:
    jobs = job_search_service.search_jobs(query=query, limit=limit)
    summary = job_search_service.summarize_jobs(jobs)
    return {
        "count": len(jobs),
        "jobs": jobs,
        "summary": summary,
    }
