from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from extensions import db, migrate, jwt
from datetime import timedelta


def create_app(config_class=Config):
    """Factory function to create Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Enable CORS
    app.config["DEBUG"] = True  # o usa app.debug directamente
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    if app.debug:
        CORS(app)
    else:
        CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.files import files_bp
    from routes.ledger_analysis import ledger_analysis_bp
    from routes.user_settings import user_settings_bp
    from routes.notifications import notifications_bp
    from routes.news import news_bp
    from routes.user_activity import activity_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(files_bp, url_prefix="/files")
    app.register_blueprint(ledger_analysis_bp, url_prefix="/ledger")
    app.register_blueprint(user_settings_bp, url_prefix="/users")
    app.register_blueprint(notifications_bp, url_prefix="/users")
    app.register_blueprint(news_bp, url_prefix="/news")
    app.register_blueprint(activity_bp, url_prefix="/activity")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(app.config.get("PORT", 5000)),
        debug=True,
        use_reloader=True,
    )
