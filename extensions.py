import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import CLIENT_ID, CLIENT_PASS, REDIRECT, scope
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_PASS, redirect_uri=REDIRECT,
                                               scope=scope, show_dialog=True, cache_path='token.txt'))
db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
