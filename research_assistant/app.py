# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys
from flask import Flask
from flask import jsonify
from flask_cors import CORS

from sqlalchemy import inspect
import os
from research_assistant.brain.views import brainstorm_bp
from research_assistant.chat.views  import chat_bp
from research_assistant.outline.views import outline_bp
from research_assistant import commands, public, user
from research_assistant.planning.views import planning_bp
from research_assistant.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    login_manager,
    migrate,
    mail,
    jwt,
    init_s3_client
)
from research_assistant.public.views import blueprint
from research_assistant.dashboard.views import dashboard as dashboard_blueprint
from research_assistant.tag.views import blueprint as tag_bp
from research_assistant.ai_assistant.views import blueprint as ai_bp
from research_assistant.public.views import blueprint
from research_assistant.dashboard.views import dashboard as dashboard_blueprint
from research_assistant.writing_tool.routes import writing_tool_bp 

def create_app(config_object="research_assistant.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    if os.getenv("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

    register_extensions(app)
    app.register_blueprint(writing_tool_bp, url_prefix="/writing_tool")
    csrf_protect.exempt(writing_tool_bp)
    csrf_protect.exempt(blueprint)
    mail.init_app(app)
    init_s3_client(app)
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names(schema='public')
            print("Tables in public schema:", tables)
            if "users" not in tables:
                db.create_all()
        except Exception as e:
            print("⚠️ Warning: could not inspect/create tables:", e)

    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
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
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
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
    """
    Register error handlers that return JSON responses instead of rendering templates.
    """
    def render_error(error):
        """Return a JSON error response for API clients."""
        error_code = getattr(error, "code", 500)
        error_msg = getattr(error, "description", "Server Error")
        return jsonify({
            "code": error_code,
            "msg": error_msg
        }), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
