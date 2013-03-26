import logging

from flask import Flask
from flask.ext.assets import Bundle, Environment


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        ADMINS=['zak@madebycabin.com'],
        SMTP_HOST='email-smtp.us-east-1.amazonaws.com',
        SMTP_FROM='Collate <xo@madebycabin.com>',
    )
    app.config.from_pyfile('settings.cfg')
    configure_logging(app)
    assets = register_assets(app)
    if app.debug:
        register_specs(app, assets)
    app.context_processor(lambda: {
        'debug': app.debug,
    })
    return app


def configure_logging(app):
    if not app.debug:
        admins = app.config['ADMINS']
        if isinstance(admins, basestring):
            admins = [admins]
        mail_handler = logging.handlers.SMTPHandler(
            mailhost=app.config['SMTP_HOST'],
            fromaddr=app.config['SMTP_FROM'], toaddrs=admins,
            subject='Error',
            credentials=app.config.get('SMTP_CREDENTIALS'), secure=())
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    # StreamHandler is suitable for the dev server and uWSGI.
    handler = logging.StreamHandler()
    app.logger.addHandler(handler)


def register_assets(app):
    assets = Environment(app)
    assets.auto_build = app.debug
    assets.manifest = 'file'
    assets.register(
        'screen.css',
        'vendor/normalize-2.1.0.css',
        filters='cssmin', output='gen/screen-%(version)s.css')
    assets.register(
        'vendor.js',
        'vendor/jquery-1.9.1.js',
        'vendor/underscore-1.4.4.js',
        'vendor/backbone-1.0.0.js',
        filters='uglifyjs', output='gen/vendor-%(version)s.js')
    # Modernizr bootstraps the other assets, so it must be separate.
    assets.register(
        'modernizr.js',
        'vendor/modernizr.js',
        output='gen/modernizr-%(version)s.js')
    return assets


def register_specs(app, assets):
    from flask.ext.jasmine import Asset, Jasmine
    # TODO: once Flask-Assets >0.8 is out, use assets.append_path instead of
    # this hack. See https://github.com/miracle2k/flask-assets/issues/35.
    assets.register(
        'specs', '../../specs/*.coffee', '../../specs/**/*.coffee',
        filters='coffeescript', output='gen/specs.js')
    jasmine = Jasmine(app)
    jasmine.specs(Asset('specs'))
    jasmine.sources(Asset('vendor.js'))
