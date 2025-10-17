from flask import Blueprint, request, jsonify, current_app
from ..utils.storage import save_json, CONFIG_PATH
from ..utils.helpers import append_log, now_iso

fan_bp = Blueprint("fan", __name__, url_prefix="/fan")

@fan_bp.post("/toggle")
def fan_toggle():
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id")
    state = (data.get("state") or "").lower()
    cfg = current_app.config["CONFIG_DATA"]
    dev = cfg["devices"].get(device_id)
    if not dev:
        return jsonify({"ok": False, "error": "unknown_device"}), 404
    dev["desired_state"] = state
    save_json(CONFIG_PATH, cfg)
    append_log({"type": "control", "device_id": device_id, "command": state})
    return jsonify({"ok": True, "desired_state": state})
