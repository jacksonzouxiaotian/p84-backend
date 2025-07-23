from research_assistant.extensions import db

class UserSettings(db.Model):
    __tablename__ = "user_settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    language = db.Column(db.String(20), default="en")
    theme = db.Column(db.String(20), default="light")
    notifications_enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "language": self.language,
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
        }
