from dotenv import load_dotenv
import os
import redis

load_dotenv()

class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]


    SERVER_NAME = '192.168.1.16:5000'
    SESSION_COOKIE_DOMAIN = '192.168.1.16:5000'
    SESSION_COOKIIE_SAMESITE ="None"
    SESSION_COOKIE_SERCURE = True


    SESSION_TYPE = "redis"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")