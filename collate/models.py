import os.path
from urlparse import urlparse

from flask import current_app
from flask.ext import login
from PIL import Image
import requests
from sqlalchemy import event
from StringIO import StringIO
from werkzeug import FileStorage

from collate import db, photos
from collate.util import image
from collate.util.decl_enum import DeclEnum


class User(db.Model, login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)

    def __repr__(self):
        return 'User(email=%r)' % self.email

    def check_password(self, pw):
        return pw == 'foo'  # XXX


class Moodboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    items = db.relationship('Item', backref='board', lazy='dynamic')

    def __repr__(self):
        return 'Moodboard(%r)' % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            # XXX owner
        }

    # XXX how to handle moodboards owned by organizations? perhaps they still
    # get a user owner, but they can also get an organization field.
    #owner = db.relationship('User', backref='moodboards', lazy='dynamic')


class ItemOrientationType(DeclEnum):
    landscape = 'l', 'Landscape'
    portrait = 'p', 'Portrait'


# XXX Content? Item? Record?
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('moodboard.id'))
    source_url = db.Column(db.Text)
    caption = db.Column(db.String(256))
    full_filename = db.Column(db.String(128))
    square_filename = db.Column(db.String(128))
    midsize_filename = db.Column(db.String(128))
    midsize_height = db.Column(db.Integer)
    #orientation = db.Column(ItemOrientationType.db_type())
    #crop_offset = db.Column(db.Integer(unsigned=True))

    def __repr__(self):
        return 'Item(board_id=%r, caption=%r)' % (self.board_id, self.caption)

    def serialize(self):
        return {
            'id': self.id,
            'board': self.board.serialize(),
            'source_url': self.source_url,
            'caption': self.caption,
            'full_url': photos.url(self.full_filename),
            'square_url': photos.url(self.square_filename),
            'midsize_url': photos.url(self.midsize_filename),
            'midsize_height': photos.url(self.midsize_height),
            #'orientation': self.orientation.name if self.orientation else None,
            #'crop_offset': self.crop_offset,
        }

    # XXX anywhere photos.save happens, make sure we are coercing the filename
    # to something interesting/useful. <base36 itemid>-filename?
    def build_images(self, storage):
        """Create and save all necessary image sizes."""
        # Full size.
        self.full_filename = photos.save(storage)
        base_filename, _ = os.path.splitext(storage.filename)

        # Square crop.
        storage.seek(0)
        im = Image.open(storage.stream)
        im = image.square(im, current_app.config['THUMBNAIL_SIZE'])
        square = image.to_storage(im, base_filename + '-s.jpg')
        self.square_filename = photos.save(square)

        # Midsize crop maintaining aspect ratio.
        storage.seek(0)
        im = Image.open(storage.stream)
        im = image.constrain_width(im, current_app.config['THUMBNAIL_SIZE'])
        midsize = image.to_storage(im, base_filename + '-m.jpg')
        self.midsize_filename = photos.save(midsize)
        self.midsize_height = im.size[1]

    def fetch_source_url(self):
        r = requests.get(self.source_url)
        from pprint import pprint as p
        p(r.status_code)
        p(r.headers)
        p(dir(r))
        if r.status_code != requests.codes.ok:
            r.raise_for_status()  # XXX raises requests.exceptions.HTTPError
        content_type = r.headers['Content-Type']
        if content_type.startswith('image/'):
            # XXX base36?
            filename = os.path.basename(urlparse(self.source_url).path)
            content = StringIO(r.content)
            storage = FileStorage(content, filename, content_type=content_type)
            self.build_images(storage)


def cleanup_item(mapper, connection, item):
    pass  # XXX remove item.full_filename, item.thumbnail_filename
event.listen(Item, 'before_delete', cleanup_item)
