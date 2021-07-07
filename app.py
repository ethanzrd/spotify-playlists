from flask import Flask, render_template, request, flash, url_for, redirect, session
from flask_login import current_user, login_required, logout_user

from extensions import db, login_manager, bootstrap
from functions import validate_login, register_user, get_titles, create_playlist, add_playlist
from wrappers import logout_required
from models import Playlist
from utils import generate_date


def create_app(config_file='app_config.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        requested_user = User.query.get(user_id)
        return requested_user

    return app


app = create_app()
app.app_context().push()
from models import User

db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    print(session)
    if request.method == 'POST':
        given_date = request.form['date']
        if given_date:
            if current_user.is_authenticated:
                existing_playlist = Playlist.query.filter_by(user=current_user, original_date=given_date).first()
                if existing_playlist:
                    flash("This date already exists.")
                    return redirect(url_for('index'))
            else:
                playlists = list(session.get('playlists', {}).values())
                print(playlists)
                for playlist in playlists:
                    if playlist['original_date'] == given_date:
                        flash("This date already exists.")
                        return redirect(url_for('index'))
            uris = get_titles(given_date)
            if not uris:
                flash("Could not find any songs.")
                return redirect(url_for('index'))
            playlist_link = create_playlist(uris, given_date)
            if not current_user.is_authenticated:
                if 'playlists' not in session:
                    session['playlists'] = {}
                session['playlists'][given_date] = {'original_date': given_date, 'date': generate_date(given_date),
                                                    'link': playlist_link}
                return redirect(url_for('index'))
            else:
                return add_playlist(date=given_date, link=playlist_link)
        else:
            flash("Please enter a valid date.")
            return redirect(url_for('index'))
    else:
        if not current_user.is_authenticated:
            playlists = list(session.get('playlists', {}).values())
        else:
            playlists = current_user.playlists
        return render_template('index.html', playlists=playlists)


@app.route('/delete-playlist/<original_date>')
def delete_playlist(original_date):
    if current_user.is_authenticated:
        requested_playlist = Playlist.query.filter_by(user=current_user, original_date=original_date).first()
        if requested_playlist:
            db.session.delete(requested_playlist)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash("The requested playlist could not be found.")
            return redirect(url_for('index'))
    else:
        print(session)
        if original_date in session.get('playlists', {}):
            session['playlists'].pop(original_date)
            return redirect(url_for('index'))
        else:
            flash("The requested playlist could not be found.")
            return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        required_fields = ['email', 'password']
        for field in required_fields:
            if not request.form[field]:
                flash("Please fill all required fields.")
                return redirect(url_for('login'))
        return validate_login(request.form['email'], request.form['password'])
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not request.form[field]:
                flash("Please fill all required fields.")
                return redirect(url_for('register'))
        return register_user(request.form['name'], request.form['email'], request.form['password'])
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=8050)
