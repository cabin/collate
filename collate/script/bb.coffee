class Item extends Backbone.Model

  saveFile: (file) ->
    # Build a data URI from the dropped image to serve as a placeholder.
    reader = new FileReader
    reader.addEventListener 'load', (event) =>
      @set('thumbnail_url', event.target.result)
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
        socket.emit('add-item', @toJSON())
      else
        throw 'XXX saveFile failed'

    formData = new FormData
    formData.append('image', file)
    xhr.send(formData)


class @ItemCollection extends Backbone.Collection
  model: Item

  initialize: (models, options) ->
    # XXX we should probably use a board model at some point
    @url = "/board/#{options.board_id}/items"


class @GridView extends HierView
  tagName: 'div'
  className: 'grid'

  initialize: ->
    # Ignore drops outside the container. TODO: show an error message.
    ignoreEvent = (event) -> event.preventDefault()
    document.ondragover = document.ondrop = ignoreEvent
    unless Modernizr.draganddrop
      # We need drag/drop and formdata (network-xhr2); otherwise just add a
      # simple file upload control at the bottom of the view.
      # ... with dragandrop but without xhr2, we could still support dropping
      # URLs, just not files.
      alert('no drag and drop')  # XXX

  render: (items) ->
    @$el.empty()
    frag = document.createDocumentFragment()
    items.each (item) =>
      frag.appendChild(@renderChild(new GridItemView(model: item)))
    @el.appendChild(frag)
    this

  append: (item) =>
    @$el.append(@renderChild(new GridItemView(model: item)))

  events:
    'dragover': 'dragOver'
    'dragenter': 'dragEnter'
    'dragleave': 'dragLeave'
    'drop': 'drop'

  dragEnter: (event) ->
    event.stopPropagation()
    event.preventDefault()
    @$el.addClass('drag')

  # Unused, but necessary to catch the drop event.
  dragOver: (event) ->
    event.stopPropagation()
    event.preventDefault()

  dragLeave: (event) ->
    event?.stopPropagation()
    event?.preventDefault()
    @$el.removeClass('drag')

  # Create a dummy placeholder model appended to the grid container, with image
  # source as the filedata. call savefile to actually upload and create the
  # model on the server; savefile uploads non-json (any starting attributes as
  # well) and the file, then updates the model on successful completion.
  # XXX where to put progress handler? maybe fire event on model so view can
  # handle it.
  drop: (event) ->
    event.stopPropagation()
    event.preventDefault()
    files = event.dataTransfer.files
    url = event.dataTransfer.getData('URL')
    if files.length
      _(files.length).times (n) ->
        item = new Item
        app.items.add(item)
        item.saveFile(files.item(n))
    else if url
      # handle dropped URL
      console.log(url)
    else
      throw 'XXX drag and drop not supported?'
    @dragLeave()


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
    data['offset-direction'] = @offsetDirections[data.orientation]
    @$el.html(@template(data))
    # XXX maybe if it doesn't have an ID yet? or some other indicator
    @$el.toggleClass('new', not _(data).has('orientation'))
    this

  update: =>
    @$el.find('img').attr('src', @model.get('thumbnail_url'))
    #@$el.removeClass('new')
    orientation = @model.get('orientation')
    if orientation
      @$el.find('img')
        .addClass(orientation)
        .css(@offsetDirections[orientation], "-#{@model.get('offset')}px")
