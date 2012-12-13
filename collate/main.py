from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    session,
)
from flask.views import MethodView

from collate import db, photos
from collate.models import Moodboard, Item, User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    users = User.query.all()
    board = Moodboard.query.get(1)
    return render_template('index.html', board=board, items=[], users=users)


@main.route('/board/<int:board_id>')
def board(board_id):
    board = Moodboard.query.get_or_404(board_id)
    items = [item.serialize() for item in board.items.all()]
    return render_template('index.html', board=board, items=items)


# XXX auth!
class BoardItems(MethodView):

    # This is just a ghetto WTForm. TODO: is it worth using an actual form?
    def sanitize(self, data):
        sanitized = {}
        attributes = ('source_url', 'caption')
        for attr in attributes:
            if attr in data:
                sanitized[attr] = data[attr]
        return sanitized

    def get(self, board_id, item_id):
        item = Item.query.get_or_404(item_id)
        if item.board_id != board_id:
            abort(404)
        return jsonify(item.serialize())

    def post(self, board_id):
        board = Moodboard.query.get_or_404(board_id)
        data = self.sanitize(request.json or request.data)
        data['board_id'] = board.id
        item = Item(**data)
        if 'image' in request.files:
            item.full_filename = photos.save(request.files['image'])
            item.create_thumbnail(request.files['image'])
        db.session.add(item)
        db.session.commit()
        return jsonify(item.serialize())

    def put(self, board_id, item_id):
        item = Item.query.get_or_404(item_id)
        if item.board_id != board_id:
            abort(404)
        # XXX verify any other columns?
        column_names = [c.name for c in item.__table__.columns
                        if not c.primary_key]
        # XXX save!

board_items_view = BoardItems.as_view('board_items')
main.add_url_rule('/board/<int:board_id>/items',
                   view_func=board_items_view, methods=['POST'])
main.add_url_rule('/board/<int:board_id>/items/<int:item_id>',
                   view_func=board_items_view, methods=['GET, PUT'])



@main.route('/upload', methods=['POST'])
def upload():
    from collate import photos

    urls = []
    if 'file' in request.files:
        for f in request.files.getlist('file'):
            #XXX
            filename = f.filename
            #filename = photos.save(f)
            #item = Item(filename=filename)
            #db.session.add(item)
            urls.append(filename)
        #db.session.commit()
        return jsonify({'success': True, 'urls': urls})

    # accept and save file (using a simple form?) and metadata
    #   original URL
    #   dimensions
    #   moodboard
    # convert to various sizes
    # upload all sizes to S3
    return jsonify({'success': False})


# TODO rename and think about this a bit harder
@main.route('/available-boards')
def available_boards():
    if 'username' not in session:
        return jsonify({'error': 'Authentication required.'}), 401
    return jsonify(dict(
        username=session['username'],
        # TODO: avatar, etc...
        boards=['Test Board'],
    ))
