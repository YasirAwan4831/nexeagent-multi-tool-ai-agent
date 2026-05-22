"""Direct utility tools API (for frontend/testing)."""

from flask import Blueprint, jsonify, request

from tools.function_tools import FUNCTION_REGISTRY
from utils.tool_runner import run_function_tool

tools_bp = Blueprint("tools", __name__, url_prefix="/api/tools")


@tools_bp.route("/list", methods=["GET"])
def list_tools():
    return jsonify({
        "success": True,
        "tools": list(FUNCTION_REGISTRY.keys()),
    })


@tools_bp.route("/<tool_name>", methods=["POST"])
def run_tool(tool_name):
    if tool_name not in FUNCTION_REGISTRY:
        return jsonify({"success": False, "error": "Unknown tool"}), 404
    data = request.get_json(silent=True) or {}
    result = run_function_tool(tool_name, data)
    if result.get("error"):
        return jsonify({"success": False, "error": result["error"]}), 400
    return jsonify({"success": True, "tool": tool_name, "result": result})
