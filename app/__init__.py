from flask import Flask
from pathlib import Path
from .utils.storage import load_json, CONFIG_PATH, LOGS_PATH
from .routes.ui import ui_bp
from .routes.notify import notify_bp



def create_app():
    app = Flask(__name__)

    # Tải dữ liệu ban đầu
    app.config["CONFIG_DATA"] = load_json(CONFIG_PATH, default={
        "passwords": {}, "rfid_cards": {}, "devices": {}, "access_rules": {}, "system_info": {}
    })
    app.config["LOGS_DATA"] = load_json(LOGS_PATH, default=[])

    # Đăng ký blueprint routes
    from .routes.access import access_bp
    from .routes.fan import fan_bp
    from .routes.overview import overview_bp

    app.register_blueprint(access_bp)
    app.register_blueprint(fan_bp)
    app.register_blueprint(overview_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(notify_bp)

    return app
