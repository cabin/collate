# A quick re-implementation of thoughtbot's [Backbone-Support][] package that
# maps more closely to my usage.
# [Backbone-Support]: https://github.com/thoughtbot/backbone-support

#### ElementRouter
# A `Backbone.Router` used to show a single view at a time. Instances must have
# an `el` attribute, whose contents will be replaced with the rendered view
# each time `show(view)` is called. Any previous view will be removed.
class @ElementRouter extends Backbone.Router

  show: (view) ->
    @currentView?.remove()
    @currentView = view
    $(@el).empty().append(view.render().el)


#### CompositeView
# A `Backbone.View` that is aware of its subviews and removes them when it is
# removed. Use Backbone >=0.9.9's `listenTo` method to track bound events,
# which will also be removed along with the view.
class @HierView extends Backbone.View

  # Add a new tracked child view.
  addChild: (view) ->
    @_children or= []
    @_children.push(view)
    view._parent = this
    view

  # Add a new child view and render it immediately. Return the child view's
  # `el` attribute. Convenient for adding and rendering a child in one fell
  # swoop; e.g., `this.$el.append(this.renderChild(new View))`.
  renderChild: (view) ->
    @addChild(view)
    view.render().el

  # Remove all children, tell our parent (if any) to stop tracking us, then
  # delegate to `Backbone.View.remove`. If `options.ignoreParent` is true, skip
  # the parent step---useful for avoiding unnecessary bookkeeping when the
  # parent is also being removed.
  remove: (options = {}) ->
    _(@_children).invoke('remove', ignoreParent: true)
    @_parent?._emancipate?(this) unless options.ignoreParent
    super()

  # Stop tracking the given child.
  _emancipate: (child) ->
    @_children = _(@_children).without(child)


#### DropHandler
# A `Backbone.View` that creates the necessary event handlers for drag and drop
# on the document. Passing in a different `el` will listen to drag and drop on
# that element instead, while ignoring drops on the document itself.
class @DropHandler extends Backbone.View
  el: document

  initialize: ->
    jQuery.event.props.push('dataTransfer')
    @classableEl = @$el
    # Make sure we can add a class while dragging.
    if @el is document
      @classableEl = $(document).find('body').first()
    # Ignore drops outside the container.  # XXX verify this
    else
      ignoreEvent = (event) -> event.preventDefault()
      document.ondragover = document.ondrop = ignoreEvent
    @enteredElements = 0

  events:
    'dragenter': 'dragEnter'
    'dragover': 'cancel'  # necessary to catch the drop element
    'dragleave': 'dragLeave'
    'drop': 'drop'

  cancel: (event) ->
    event.stopPropagation()
    event.preventDefault()

  dragEnter: (event) ->
    @cancel(event)
    @enteredElements += 1
    @classableEl.addClass('drag')

  dragLeave: (event) ->
    @cancel(event)
    @enteredElements -= 1
    @classableEl.removeClass('drag') if @enteredElements is 0

  drop: (event) ->
    @cancel(event)
    @classableEl.removeClass('drag')
    @trigger('drop', event)
