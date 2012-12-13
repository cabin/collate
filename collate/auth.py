from flask import Blueprint, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from flask.ext.wtf import BooleanField, PasswordField, validators
from flask.ext.wtf.html5 import EmailField

from collate import login_manager
from collate.models import User
from collate.util.redirect_form import RedirectForm

auth = Blueprint('auth', __name__)


class LoginForm(RedirectForm):
    email = EmailField(validators=[validators.Required()])
    password = PasswordField(validators=[validators.Required()])
    remember = BooleanField('Remember me')

    def validate(self):
        rv = super(LoginForm, self).validate()
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append(
                "We don't have that email address on file!")
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Incorrect password.')
            return False

        self.user = user
        return True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        return form.redirect('main.index')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# TODO
# consider using alternative tokens including a password hash (get_auth_token,
# make_secure_token, token_loader)
