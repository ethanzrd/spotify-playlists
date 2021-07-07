import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'string')
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///spotify_playlists.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
