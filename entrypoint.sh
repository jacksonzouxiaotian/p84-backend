#!/bin/sh
exec gunicorn -b 0.0.0.0:${PORT:-5000} autoapp:app
