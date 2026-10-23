"""Vercel Serverless Function Entry Point for Smart Data Quality Analyzer API."""

import sys
import os

# Ensure backend directory is discoverable in Python sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "..", "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

# Vercel ASGI Handler exposes the FastAPI app object
__all__ = ["app"]
