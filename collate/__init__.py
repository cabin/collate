from flask import Flask
from flask.ext.assets import Bundle, Environment


def create_app():
    app = Flask(__name__)
    register_assets(app)
    return app


def register_assets(app):
    assets = Environment(app)
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
