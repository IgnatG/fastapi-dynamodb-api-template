"""
AWS Lambda deployment handler.

This file is ONLY used when deploying to AWS Lambda.
"""

from mangum import Mangum
from app.application import get_app

app = get_app()

# Mangum acts as a bridge between Lambda and FastAPI
handler = Mangum(app, lifespan="off")
