"""Shared dispatcher for function registry tools."""

from tools.function_tools import FUNCTION_REGISTRY


def run_function_tool(name: str, args: dict | None = None, fallback_text: str = "") -> dict:
    """Execute a registered utility tool with normalized arguments."""
    if name not in FUNCTION_REGISTRY:
        return {"error": f"Unknown tool: {name}"}

    args = args or {}
    fn = FUNCTION_REGISTRY[name]

    try:
        if name == "datetime_tool":
            return fn()
        if name == "calculator":
            return fn(args.get("expression", "0"))
        if name in ("text_summarizer", "url_extractor", "keyword_extractor", "text_cleaner"):
            return fn(args.get("text") or fallback_text)
        if name == "json_formatter":
            return fn(args.get("text", "{}"))
        if name == "search_optimizer":
            return fn(args.get("query") or fallback_text)
        if name == "job_filter":
            return fn(
                jobs=args.get("jobs", []),
                keyword=args.get("keyword", ""),
            )
        return fn(**{k: v for k, v in args.items() if k in fn.__code__.co_varnames})
    except TypeError as exc:
        return {"error": f"Invalid arguments for {name}: {exc}"}
    except Exception as exc:
        return {"error": str(exc)}
