import datetime

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename, redirect
from forms.RegisterForm import RegisterForm
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mirox_secretkey'


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



if __name__ == "__main__":
    db_session.global_init("db/mirox_db.db")
    app.run()
