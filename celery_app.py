from celery import Celery
import time
from dotenv import load_dotenv
import os


load_dotenv()

celery = Celery(
    "worker",  
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"), 
    backend=os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379/0"),
)


import tasks