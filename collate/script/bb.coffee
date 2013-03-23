class @Board extends Backbone.Model
  url: -> "/board/#{@get('id')}"


class Item extends Backbone.Model

  saveFile: (file) ->
    # Build a data URI from the dropped image to serve as a placeholder.
    reader = new FileReader
    reader.addEventListener 'load', (event) =>
      @set('square_url', event.target.result)
    reader.readAsDataURL(file)

    # Save asynchronously.
    xhr = new XMLHttpRequest
    xhr.open('POST', _.result(this, 'url'))
    xhr.setRequestHeader('Accept', 'application/json')
    xhr.addEventListener 'progress', (event) ->
      console.log('progress', event)

    xhr.addEventListener 'load', (event) =>
      if xhr.status is 200
        data = JSON.parse(xhr.response)
        @set(data)
        socket?.emit('add-item', @toJSON())
      else
        throw 'XXX saveFile failed'

    formData = new FormData
    formData.append('image', file)
    xhr.send(formData)


class @ItemCollection extends Backbone.Collection
  model: Item
  url: -> @board.url() + '/items'

  initialize: (models, options) ->
    @board = options.board


class @GridView extends HierView
  className: 'grid'
  # TODO: compute these from CSS?
  figureSize: 230
  gutterSize: 20

  initialize: ->
    @listenTo(@collection, 'add', @append)
    @listenTo(app.dropHandler, 'drop', @drop)
    $(window).on('resize.gridview', _.debounce(@resize, 10))
    unless Modernizr.draganddrop
      # We need drag/drop and formdata (network-xhr2); otherwise just add a
      # simple file upload control at the bottom of the view.
      # ... with dragandrop but without xhr2, we could still support dropping
      # URLs, just not files.
      alert('no drag and drop')  # XXX

  remove: ->
    $(window).off('resize.gridview')
    super()

  render: ->
    _.defer(@resize)
    @$el.empty()
    frag = document.createDocumentFragment()
    @collection.each (item) =>
      frag.appendChild(@renderChild(new GridItemView(model: item)))
    @el.appendChild(frag)
    this

  append: (item) =>
    @$el.append(@renderChild(new GridItemView(model: item)))

  resize: =>
    console.count('resize')
    maxWidth = @$el.wrap('<div>').parent().width()
    @$el.unwrap()
    width = 0
    # Find the maximal number of items we can show in the available width.
    _(_.range(1, 21)).find (n) =>
      w = @figureSize * n + @gutterSize * (n + 1)
      width = w unless w > maxWidth
      # Stop searching on the first n that is too big.
      return w > maxWidth
    # Reduce width by one gutterSize, as that is handled by padding.
    @$el.width(width - @gutterSize)

  drop: (event) ->
    files = event.dataTransfer.files
    url = event.dataTransfer.getData('URL')
    if files.length
      _(files.length).times (n) ->
        item = new Item
        app.items.add(item)
        item.saveFile(files.item(n))
    else if url
      console.log('dropped url', url)
      app.items.create(source_url: url)
    else
      throw 'XXX drag and drop not supported?'


class GridItemView extends HierView
  tagName: 'figure'
  template: Handlebars.templates['grid-item']
  offsetDirections:
    landscape: 'left'
    portrait: 'top'

  initialize: ->
    #@bindTo(@model, 'change:thumbnail_url', @render)
    @listenTo(@model, 'change', @render)
    # XXX update? no point in changing thumbnail_url once it's set once... want
    # to transition .new -> no-class rather than re-render for transition, etc.
    # actually, maybe want to preload the new thumbnail_url to prime caches for
    # reloading, but still don't bother to update the rendered view

  render: ->
    data = @model.toJSON()
    @$el.html(@template(data))
    @$el.toggleClass('loading', @model.isNew())
    this

  update: =>
    @$el.find('img').attr('src', @model.get('square_url'))
    #@$el.removeClass('new')
    ###
    orientation = @model.get('orientation')
    if orientation
      @$el.find('img')
        .addClass(orientation)
        .css(@offsetDirections[orientation], "-#{@model.get('offset')}px")
    ###


class SidebarView extends HierView
  className: 'sidebar'
  template: Handlebars.templates.sidebar

  render: ->
    @$el.html(@template())
    this

  events:
    'click .toggle': 'toggle'
    'click .stats': 'stats'
    'click .collaborators': 'collaborators'
    'click .chat': 'chat'

  toggle: (event) ->
    console.log('toggle', arguments)
    @$el.toggleClass('out')

  stats: (event) ->
    console.log('stats', arguments)

  collaborators: (event) ->
    console.log('collaborators', arguments)

  chat: (event) ->
    console.log('chat', arguments)


class @BoardRouter extends Backbone.Router

  initialize: (@board, @items) ->
    # XXX bind dnd events on document
    #Backbone.history.start(pushState: true, root: "/board/#{board_id}")
    @dropHandler = new DropHandler()

  routes:
    '': 'grid'
    'grid': 'grid'
    'columns': 'columns'
    'view/:id': 'detail'

  grid: ->
    sidebar = new SidebarView(model: @board).render()
    sidebar.$el.appendTo('.content')
    view = new GridView(collection: @items).render()
    view.$el.appendTo('.content')

  columns: ->
    console.log('columns')

  detail: (id) ->
    console.log('detail', arguments)
