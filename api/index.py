"""Vercel Python entrypoint: exposes the existing FastAPI ASGI app for the @vercel/python builder."""
from backend.main import app
