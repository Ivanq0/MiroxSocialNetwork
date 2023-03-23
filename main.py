import datetime

from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename, redirect
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from data import db_session
from data.users import User
from data.profile_pictures import ProfilePicture

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mirox_secretkey'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('base.html', title="MiroxSN")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            date_of_birth=form.date_of_birth.data,
            created_date=datetime.datetime.today()
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']

    if not pic:
        return "No pfp uploaded", 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    img = ProfilePicture(img=pic.read(), mimetype=mimetype, name=filename, user_id=current_user.id)
    db_sess = db_session.create_session()
    if db_sess.query(ProfilePicture).filter(ProfilePicture.user_id == current_user.id).first():
        img_to_del = db_sess.query(ProfilePicture).filter(ProfilePicture.user_id == current_user.id).first()
        db_sess.delete(img_to_del)
    db_sess.add(img)
    db_sess.commit()

    return "Pfp has been uploaded!", 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/upload_pfp')
@login_required
def test():
    return render_template("upload_pfp.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init("db/mirox_db.db")
    app.run()
