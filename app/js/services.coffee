angular.module('collate.services', [])

  .factory 'websocket', ($window) ->
    url = "ws://#{$window.location.host}/ws"
    conn = new golem.Connection(url)

    console.log 'connecting...', url

    conn.on 'answer', (data) ->
      console.log('got an answer:', data.msg, data.username)

    conn.on 'open', ->
      console.log 'opened'
      conn.emit 'identify', from: 'jimbo'
      conn.emit 'hello', from: 'nobody'
