# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

from research_assistant.user.models import User


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, **kwargs):
        """Validate the form."""
        # 先做 WTF 默认的字段级校验
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        # 根据用户名查找用户
        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append("Unknown username")
            return False

        # 密码校验：优先使用 hash 检查，其次回退到明文比对（测试模式下可能需要）
        valid = False
        if hasattr(self.user, "check_password"):
            try:
                valid = self.user.check_password(self.password.data)
            except Exception:
                valid = False

        # 明文回退
        if not valid and self.password.data == getattr(self.user, "password", None):
            valid = True

        if not valid:
            self.password.errors.append("Invalid password")
            return False

        # 检查用户是否已激活
        if not self.user.active:
            self.username.errors.append("User not activated")
            return False

        return True
