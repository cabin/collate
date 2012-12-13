http = require('http')
url = require('url')

io = require('socket.io').listen(5010)


# TODO: nginx (1.2+) proxy_pass: use a sub-URL
#       OR use a subdomain... but then sharing cookies? maybe I don't need to
#       share cookies at all --- I can send the cookie data along in the
#       connection request.

io.configure 'production', ->
  io.enable('browser client minification')
  io.enable('browser client etag')
  io.enable('browser client gzip')
  io.enable('match origin protocol')
  io.set('log level', 1)
  # Uncomment this block to enable flashsocket; otherwise it's defaults.
  #io.set 'transports', [
  #  'websocket'
  #  'flashsocket'
  #  'htmlfile'
  #  'xhr-polling'
  #  'jsonp-polling'
  #]


###
 disabled authorization because we can't access the socket here anyway; may as
 well wait for a join message
io.configure ->
  io.set 'authorization', (handshakeData, callback) ->
    error = null  # or String
    authorized = false
    console.log(handshakeData.query)


    options = url.parse('http://collate.dev/available-boards')
    options.headers =
      Cookie: "session=#{handshakeData.query.session}"
    http.get options, (res) ->
      if res.statusCode is 200
        authorized = true
        output = ''
        res.on('data', (chunk) -> output += chunk)
        res.on 'end', ->
          obj = JSON.parse(output)

      console.log('-----------------')
      console.log res.statusCode
      console.dir(res)
      console.log('-----------------')
      callback(error, authorized)


    # Just throw an async isauthed function in here
    # https://github.com/LearnBoost/socket.io/wiki/Authorizing
###


# callback(isAuthed, data)
checkAuth = (room, session, callback) ->
  # XXX /board/<id>/auth
  options = url.parse('http://collate.dev/available-boards')
  options.headers =
    Cookie: "session=#{session}"
  http.get options, (res) ->
    if res.statusCode isnt 200
      return callback(false, statusCode: res.statusCode)
    output = ''
    res.on('data', (chunk) -> output += chunk)
    res.on('end', -> callback(true, JSON.parse(output)))


getUserList = (room) ->
  client.store.data.username for client in io.sockets.clients(room)


###
getJSON = (options, callback) ->
  http.get options, (res) ->
    if res.statusCode is 200
      authorized = true
      output = ''
      res.on('data', (chunk) -> output += chunk)
      res.on 'end', ->
        obj = JSON.parse(output)
###


io.sockets.on 'connection', (socket) ->
  # TODO: each board gets a "room".
  #     https://github.com/LearnBoost/socket.io/wiki/Rooms
  # TODO: ensure user is logged in and has access to the board -- how?
  #     maybe something like an itsdangerous cookie listing allowed boards?
  #     or just a user id, which I could then ask an API server about
  #         or ask redis
  #     also get the user's name/avatar/etc. at this stage
  #socket.set('name', 'XXXtestname')

  socket.on 'join', (room, session, callback) ->
    checkAuth room, session, (isAuthed, data) ->
      return unless isAuthed  # XXX TODO
      socket.join(room)
      socket.set('currentRoom', room)
      socket.set('username', data.username)
      callback(getUserList(room))

    # TODO: fail if the socket already belongs to a room?
    #socket.join(room)
    #socket.set('currentRoom', room)
    #socket.set('name', name)
    #io.sockets.emit('join', name)
    #console.log(io.sockets.manager)
    #console.log('---------------------')
    #console.dir(socket)
    #
    # list of rooms this client has joined:
    # io.sockets.manager.roomClients[socket.id]
    # list of all rooms on the server:
    # io.sockets.manager.rooms
    # list of clients in a room:
    # io.sockets.clients('room')
    #
  # emitting to a room:
  # socket.get 'currentRoom', (err, room) ->
  #   io.sockets.in(room).emit(...)
  #
  #
  socket.on 'getUserList', (callback) ->
    socket.get 'currentRoom', (err, room) -> callback(getUserList(room))

  socket.on 'say', (msg) ->
    socket.get 'currentRoom', (err, room) ->
      socket.get 'username', (err, username) ->
        io.sockets.in(room).emit('say', username, msg)

  socket.on 'add-item', (item) ->
    socket.get 'currentRoom', (err, room) ->
      io.sockets.in(room).emit('add-item', item)

  socket.on 'msg', (msg) ->
    socket.get 'name', (err, name) ->
      io.sockets.emit('msg', name, msg)

  socket.on 'disconnect', ->
    socket.get 'name', (err, name) ->
      io.sockets.emit('leave', name)

  socket.on 'subscribe', (data) ->
    console.log('subscribe', data)

  socket.on 'message', (data) ->
    console.log('message', data)
