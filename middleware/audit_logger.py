"""Cabeceras de respuesta. Los cambios se auditan en la base y los accesos en auth."""
import time
from flask import g

def audit_before_request():
    g.start_time = time.monotonic()

def audit_after_request(response):
    response.headers["X-Response-Time-Ms"] = str(int((time.monotonic() - g.start_time) * 1000))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response
