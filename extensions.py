"""
===============================================================================
EVENTOS-UNI - MÓDULO DE EXTENSIONES FLASK
===============================================================================
Instanciación centralizada de extensiones Flask para evitar importaciones circulares.
===============================================================================
"""

from flask_caching import Cache
from flask_mail import Mail

cache = Cache()
mail = Mail()
