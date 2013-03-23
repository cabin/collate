from flask.ext.wtf import Form



from flask.ext.wtf import BooleanField, PasswordField, validators
from flask.ext.wtf.html5 import EmailField



class ItemForm(Form):
    source_url = db.Column(db.Text)
    caption = db.Column(db.String(256))

# XXX



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


