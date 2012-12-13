import os.path

from flask.ext import login
from PIL import Image
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
    thumbnail_filename = db.Column(db.String(128))
    orientation = db.Column(ItemOrientationType.db_type())
    crop_offset = db.Column(db.Integer(unsigned=True))

    def __repr__(self):
        return 'Item(board_id=%r, caption=%r)' % (self.board_id, self.caption)

    def serialize(self):
        # XXX HACK
        absolute_url = photos.url(self.thumbnail_filename)
        relative_url = absolute_url.replace('http://collate.dev', '')
        return {
            'id': self.id,
            'board': self.board.serialize(),
            'source_url': self.source_url,
            'caption': self.caption,
            'full_url': photos.url(self.full_filename),
            #'thumbnail_url': photos.url(self.thumbnail_filename),
            'thumbnail_url': relative_url,
            'orientation': self.orientation.name if self.orientation else None,
            'crop_offset': self.crop_offset,
        }

    def create_thumbnail(self, storage):
        """Set thumbnail_filename, orientation, and crop_offset."""
        storage.seek(0)  # likely already consumed elsewhere
        im = Image.open(storage.stream)
        im = image.constrain_shortest_dimension(im, 100)
        sqof = image.square_offset(im)
        self.orientation = getattr(ItemOrientationType, sqof['orientation'])
        self.crop_offset = sqof['offset']
        # Build a new FileStorage for Flask-Uploads to save.
        outf = StringIO()
        im.save(outf, 'JPEG')
        outf.seek(0)
        filename, _ = os.path.splitext(storage.filename)
        filename += '-t.jpg'
        out = FileStorage(outf, filename, content_type='image/jpeg')
        self.thumbnail_filename = photos.save(out)


def cleanup_item(mapper, connection, item):
    pass  # XXX remove item.full_filename, item.thumbnail_filename
event.listen(Item, 'before_delete', cleanup_item)
