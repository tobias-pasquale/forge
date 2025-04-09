import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///forge.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
