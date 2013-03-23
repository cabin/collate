from flask import Flask
from flask.ext.assets import Bundle, Environment
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import IMAGES, UploadSet, configure_uploads
from redis import StrictRedis

from collate.util.s3_upload_set import S3UploadSet

#from itsdangerous_session import ItsdangerousSessionInterface

db = SQLAlchemy()
login_manager = LoginManager()
photos = UploadSet('photos', default_dest=lambda app: app.instance_path)


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.cfg')
    app.config.from_pyfile('local_settings.cfg', silent=True)

    # TODO: Remove this once it's implemented in Flask (likely 0.10).
    #app.session_interface = ItsdangerousSessionInterface()

    # XXX are we using redis?
    #app.redis = StrictRedis(db=app.config['REDIS_DB'])
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    if app.config['USE_S3']:
        # TODO: passing app.config is something of an anti-pattern, but we
        # don't have a request context to use for flask.current_app.
        global photos
        photos = S3UploadSet('photos', config=app.config)
    configure_uploads(app, [photos])
    # XXX patch_request_class?

    register_assets(app)

    from collate.auth import auth
    from collate.main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app


def register_assets(app):
    assets = Environment(app)
    assets.config['stylus_plugins'] = ['nib']
    assets.config['stylus_extra_args'] = [
        '--inline',
        '--include', '%s/style' % app.root_path,
        '--include', '%s/static' % app.root_path,
    ]

    assets.register(
        'css',
        'vendor/normalize.css',
        Bundle(
            '../style/screen.styl',
            depends='../style/*.styl',
            filters='stylus', output='gen/stylus.css'),
        #Bundle(
        #    '../sass/screen.sass',
        #    depends='../sass/_*.sass',
        #    filters='compass', output='gen/sass.css'),
        filters='cssmin', output='gen/screen.css')

    assets.register(
        'vendor.js',
        'vendor/jquery-1.8.2.js',
        #'vendor/jquery.filedrop.js',
        'vendor/underscore-1.4.3.js',
        'vendor/backbone-0.9.9.js',
        'vendor/handlebars.runtime-1.0.rc.1.js',
        filters='uglifyjs', output='gen/vendor.js')

    assets.register(
        'site.js',
        Bundle(
            '../templates/js/*',
            depends='dummy',  # TODO: remove this once webassets fix is in
            filters='handlebars', output='gen/templates.js'),
        Bundle(
            '../script/support.coffee',
            '../script/bb.coffee',
            #'../script/drop.coffee',
            filters='coffeescript', output='gen/coffee.js'),
        filters='uglifyjs', output='gen/site.js')


# XXX
def repopulate():
    db.drop_all()
    db.create_all()
    from collate.models import *

    u = User(email='zakj@nox.cx')
    db.session.add(u)
    db.session.commit()

    b = Moodboard(name='Test Board', owner_id=u.id)
    db.session.add(b)
    db.session.commit()
