# app/routes/fan.py
from flask import Blueprint, request, jsonify
from ..utils.storage import load_json, save_json, CONFIG_PATH
from ..utils.helpers import append_log, now_iso

fan_bp = Blueprint("fan", __name__, url_prefix="/fan")

@fan_bp.post("/toggle")
def fan_toggle():
    data = request.get_json(silent=True) or {}
    device_id = (data.get("device_id") or "").strip()
    state = (data.get("state") or "").lower()

    if state not in ("on", "off"):
        return jsonify({"ok": False, "error": "state_must_be_on_or_off"}), 400

    cfg = load_json(CONFIG_PATH, default={"devices": {}})
    dev = cfg.get("devices", {}).get(device_id)
    if not dev:
        return jsonify({"ok": False, "error": "unknown_device"}), 404

    dev["desired_state"] = state
    save_json(CONFIG_PATH, cfg)

    append_log({
        "type": "control",
        "device_id": device_id,
        "target": "fan",
        "command": state,
        "timestamp": now_iso()
    })

    return jsonify({
        "ok": True,
        "device_id": device_id,
        "desired_state": state,
        "message": "pending_for_gateway"
    }), 200

@fan_bp.get("/state")
def fan_state():
    device_id = (request.args.get("device_id") or "").strip()
    if not device_id:
        return jsonify({"ok": False, "error": "missing_device_id"}), 400

    cfg = load_json(CONFIG_PATH, default={"devices": {}})
    dev = cfg.get("devices", {}).get(device_id)
    if not dev:
        # 🔴 vẫn trả JSON, tránh HTML 404 khiến UI parse lỗi
        return jsonify({"ok": False, "error": "unknown_device"}), 404

    desired = dev.get("desired_state", "off")
    return jsonify({"ok": True, "device_id": device_id, "desired_state": desired, "ts": now_iso()}), 200
