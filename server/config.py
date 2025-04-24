from dotenv import load_dotenv
import os
import redis

load_dotenv()

class ApplicationConfig:
    SECRET_KEY = "asojhgvppfjkwujcmekj"
    #asojhgvppfjkwujcmekj


    #SERVER_NAME = '192.168.1.16:5000'
    SESSION_COOKIIE_SAMESITE ="None"
    SESSION_COOKIE_HTTPONLY = True
    
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    #SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")