import mimetypes

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import current_app
from flask.ext.uploads import (
    UploadNotAllowed, UploadSet, lowercase_ext, secure_filename)
from werkzeug.utils import cached_property


class S3UploadSet(UploadSet):
    """An UploadSet that saves files directly to Amazon S3."""
    acl = 'public-read'
    max_age = 60 * 60 * 24 * 365 * 10  # 10 years

    def __init__(self, *args, **kwargs):
        self.cfg = kwargs.pop('config')
        super(S3UploadSet, self).__init__(*args, **kwargs)

    # Save the first connection we create.
    @cached_property
    def bucket(self):
        conn = S3Connection(self.cfg['AWS_ACCESS_KEY_ID'],
                            self.cfg['AWS_SECRET_ACCESS_KEY'])
        bucket = conn.get_bucket(self.cfg['AWS_BUCKET_NAME'])
        return bucket

    def save(self, storage, folder=None, name=None, replace=False):
        if folder is None and name is None:
            name = storage.filename
        key_components = [self.config.destination, folder, name]
        key_name = '/'.join(filter(None, key_components))
        if not self.file_allowed(storage, key_name):
            raise UploadNotAllowed()

        key = Key(self.bucket, key_name)
        # TODO: boto replace semantics are dumb: set_contents_from_file doesn't
        # return anything whether it was successful or failed, and doesn't
        # raise an exception. we should do a self.bucket.lookup(key_name) first
        # and handle replace ourselves.
        # consider naming as md5, perhaps inside a user folder
        # bucket/photos/<user-id>/<md5>.<ext>
        # let's call self.config.destination the AWS_BUCKET_NAME?

        content_type = storage.content_type
        if content_type is None:
            content_type = mimetypes.guess_type(key_name)
        key.set_metadata('Content-Type', content_type)
        key.set_metadata('Cache-Control', 'max-age=%d, public' % self.max_age)
        # TODO: `Expires` header for HTTP/1.0?

        # Metadata cannot be changed after uploading the file contents, so this
        # should remain at the bottom of the method.
        key.set_contents_from_file(storage, policy=self.acl, replace=replace)
        return key_name

    def url(self, filename):
        # TODO: Tabo implies that this may not be reliable.
        return Key(self.bucket, filename).generate_url(3600)
