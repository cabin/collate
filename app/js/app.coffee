deps = [
  'collate.controllers'
  'collate.services'
]

angular.module('collate', deps)

  # XXX remove this once we're instantiating websocket elsewhere
  .run (websocket) ->
