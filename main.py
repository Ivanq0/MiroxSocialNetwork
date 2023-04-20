import datetime
import io
import os

from PIL import Image
from flask import Flask, render_template, request, send_file, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.utils import secure_filename, redirect

from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.PostForm import PostForm
from data import db_session, posts_resources, users_resourses
from data.users import User
from data.posts import Posts
from data.profile_pictures import ProfilePicture

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'mirox_secretkey'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    clear_img()
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).order_by(Posts.id.desc()).all()
    return render_template('feed.html', title="MiroxSN", posts=post)


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
            created_date=datetime.datetime.now()
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Posts(content=form.content.data,
                     user_id=current_user.id)
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('post.html', title='Добавить пост', form=form)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id,
                                            Posts.user_id == current_user.id
                                            ).first()
        if posts:
            form.content.data = posts.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id,
                                            Posts.user_id == current_user.id
                                            ).first()
        if posts:
            posts.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('post_edit.html',
                           title='Редактирование поста',
                           form=form
                           )


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.id == id,
                                        Posts.user_id == current_user.id
                                        ).first()
    if posts:
        db_sess.delete(posts)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')

@app.route('/account_delete/<int:id>', methods=['GET', 'POST'])
def account_delete(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id, User.id == current_user.id).first()
    posts = db_sess.query(Posts).filter(
                                        Posts.user_id == current_user.id
                                        ).all()
    if posts:
        for post in posts:
            db_sess.delete(post)
        db_sess.commit()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return logout()

@app.route('/upload', methods=['POST'])
@login_required
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
    post = Posts(content="Обновил фотографию на странице",
                 user_id=current_user.id)
    db_sess.add(post)
    db_sess.commit()

    return redirect(f'/user/{current_user.id}')


@app.route('/login', methods=['GET', 'POST'])
def login():
    clear_img()
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
    clear_img()
    return redirect("/")


@app.route('/user/<int:id>')
def profile(id):
    clear_img()
    db_sess = db_session.create_session()
    img = db_sess.query(ProfilePicture).filter(ProfilePicture.user_id == id).first()
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).order_by(Posts.id.desc()).filter(Posts.user_id == id).all()
    user = db_sess.query(User).filter(User.id == id).first()
    if img:
        image = Image.open(io.BytesIO(img.img))
        image.save("static/img/temp_img.png")
    else:
        image = Image.open("static/img/empty_img.jpg")
        image.save("static/img/temp_img.png")
    return render_template("profile.html", user_id=id, user=user, posts=post,
                           img=url_for("static", filename="img/temp_img.png"),
                           alt=url_for("static", filename="img/empty_img.jpg"))


def serve_pil_image(pil_img):
    img_io = io.StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


def clear_img():
    if "temp_img.png" in os.listdir("static/img"):
        os.remove("static/img/temp_img.png")


if __name__ == "__main__":
    db_session.global_init("db/mirox_db.db")
    api.add_resource(posts_resources.PostListResource, '/api/post')
    api.add_resource(posts_resources.PostResource, '/api/post/<int:post_id>')
    api.add_resource(users_resourses.UserListResource, '/api/user')
    api.add_resource(users_resourses.UserResource, '/api/user/<int:user_id>')
    app.run()
