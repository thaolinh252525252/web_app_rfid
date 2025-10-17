from flask import Blueprint, jsonify, current_app
from ..utils.helpers import now_iso

overview_bp = Blueprint("overview", __name__, url_prefix="/overview")

@overview_bp.get("")
def overview():
    cfg = current_app.config["CONFIG_DATA"]
    logs = current_app.config["LOGS_DATA"]
    total = len([l for l in logs if l.get("type")=="access_attempt"])
    success = len([l for l in logs if l.get("result")=="granted"])
    failed = total - success
    return jsonify({
        "gateway_id": cfg["system_info"].get("gateway_id"),
        "attempts": total,
        "success": success,
        "failed": failed,
        "now": now_iso()
    })
