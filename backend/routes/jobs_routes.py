"""Job search API routes."""

from flask import Blueprint, jsonify, request

from services.job_search_service import job_search_service

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@jobs_bp.route("/search", methods=["GET", "POST"])
def search_jobs():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        query = data.get("query", "")
        limit = int(data.get("limit", 20))
        category = data.get("category")
    else:
        query = request.args.get("query", "")
        limit = int(request.args.get("limit", 20))
        category = request.args.get("category")

    jobs = job_search_service.search_jobs(query=query or None, category=category, limit=limit)
    summary = job_search_service.summarize_jobs(jobs)
    return jsonify({
        "success": True,
        "count": len(jobs),
        "jobs": jobs,
        "summary": summary,
        "query": query or "default",
    })


@jobs_bp.route("/saved", methods=["GET"])
def saved_jobs():
    query = request.args.get("query")
    company = request.args.get("company")
    jobs = job_search_service.list_saved_jobs(query=query, company=company)
    return jsonify({"success": True, "count": len(jobs), "jobs": jobs})
