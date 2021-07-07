import requests
import lxml
from bs4 import BeautifulSoup
from flask import flash, url_for, session, abort
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import sp, db
from models import User, Playlist
from flask_login import login_user, current_user


def get_titles(date):
    def get_uris():
        uris = []
        for title in titles:
            result = sp.search(q=f"track:{title} year:{date.split('-')[0]}", type="track")
            try:
                uri = result["tracks"]["items"][0]["uri"]
                uris.append(uri)
            except IndexError:
                pass
        return uris

    billboard_url = f'https://www.billboard.com/charts/hot-100/{date}'

    response = requests.get(billboard_url)
    contents = response.text
    soup = BeautifulSoup(contents, 'lxml')
    titles = [title.getText() for title in
              soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")]
    return get_uris()


def create_playlist(uris, date):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=f'{date} Billboard 100', public=True, collaborative=False,
                                       description=f'The top 100 songs of the year {date.split("-")[0]}')
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id=playlist_id, items=uris)
    return playlist['external_urls']['spotify']


def validate_login(email, password):
    requested_user = User.query.filter_by(email=email).first()
    if requested_user:
        if check_password_hash(requested_user.password, password):
            login_user(requested_user)
            session['playlists'] = {}
            return redirect(url_for('index'))
        else:
            flash("Incorrect password.")
            return redirect(url_for('login'))
    else:
        flash("Could not find the requested user.")
        return redirect(url_for('login'))


def register_user(name, email, password):
    requested_user = User.query.filter_by(email=email).first()
    if requested_user:
        flash("This user already exists.")
        return redirect(url_for('register'))
    else:
        secure_password = generate_password_hash(password=password,
                                                 method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=email, name=name, password=secure_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session['playlists'] = {}
        return redirect(url_for('index'))


def add_playlist(date, link):
    if current_user.is_authenticated:
        new_playlist = Playlist(date=date, link=link, user=current_user)
        db.session.add(new_playlist)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return abort(401)
