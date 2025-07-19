# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import inspect

from research_assistant import commands, public, user
from research_assistant.ai_assistant.views import blueprint as ai_bp
from research_assistant.brain.views import brainstorm_bp
from research_assistant.chat.views import chat_bp
from research_assistant.dashboard.views import dashboard as dashboard_blueprint
from research_assistant.outline.views import outline_bp
from research_assistant.planning.views import planning_bp
from research_assistant.tag.views import blueprint as tag_bp
from research_assistant.writing_tool.routes import writing_tool_bp
from research_assistant.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    init_s3_client,
    jwt,
    login_manager,
    mail,
    migrate,
)


def create_app(config_object="research_assistant.settings"):
    """Create application factory."""
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)

    # 如果设置了 DATABASE_URL，则覆盖默认的 SQLAlchemy URI
    if os.getenv("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

    # 扩展初始化
    register_extensions(app)

    # 注册 Writing Tool Blueprint，并豁免 CSRF
    app.register_blueprint(writing_tool_bp, url_prefix="/writing_tool")
    csrf_protect.exempt(writing_tool_bp)

    # 注册 Public Blueprint，并豁免 CSRF
    app.register_blueprint(public.views.blueprint)
    csrf_protect.exempt(public.views.blueprint)

    # 初始化邮件和 S3 客户端
    mail.init_app(app)
    init_s3_client(app)

    # 启动时尝试检查或创建表，不影响启动
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names(schema="public")
            app.logger.info("Tables in public schema: %s", tables)
            if "users" not in tables:
                db.create_all()
        except Exception as e:
            app.logger.warning(
                "Skipping table inspection on startup; will create_all later if needed",
                exc_info=e,
            )

    # 注册其余蓝图
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)

    # 强制打开调试及异常向上抛出
    app.config["DEBUG"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    jwt.init_app(app)
    return None


def register_blueprints(app):
    """Register additional Flask blueprints."""
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(tag_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(brainstorm_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(outline_bp)
    app.register_blueprint(planning_bp)
    return None


def register_errorhandlers(app):
    """Register JSON error handlers."""
    def render_error(error):
        code = getattr(error, "code", 500)
        desc = getattr(error, "description", "Server Error")
        return jsonify({"code": code, "msg": desc}), code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        return {"db": db, "User": user.models.User}
    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure app logger to use stdout."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)


# 应用工厂：生产环境里不直接执行 create_app()
# 只有在本地直接运行时才加载
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
