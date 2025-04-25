from dotenv import load_dotenv
import os
import redis

load_dotenv()

class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]

    SESSION_COOKIIE_SAMESITE ="None"
    SESSION_COOKIE_HTTPONLY = True
    
    SESSION_USE_SIGNER = True
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")