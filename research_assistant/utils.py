# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import current_app, flash

from research_assistant.extensions import get_s3_client


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


def upload_file_to_s3(file_storage, key_name, bucket_name=None):
    """Upload a file object to S3 and return the key name."""
    s3_client = get_s3_client()

    if not bucket_name:
        bucket_name = current_app.config["AWS_S3_BUCKET_NAME"]

    s3_client.upload_fileobj(file_storage, bucket_name, key_name)
    return key_name
