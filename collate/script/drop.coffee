f = ->
  $('.grid').filedrop
    url: URLS.upload,
    paramname: 'file'
    error: (err, file) ->
        switch err
          when 'BrowserNotSupported'
            console.log('browser does not support html5 drag and drop', file)
          when 'TooManyFiles'
            # user uploaded more than 'maxfiles'
            console.log('Error: TooManyFiles')
          when 'FileTooLarge'
            # program encountered a file whose size is greater than
            # 'maxfilesize' FileTooLarge also has access to the file which was
            # too large use file.name to reference the filename of the culprit
            # file
            console.log('Error: FileTooLarge')
          when 'FileTypeNotAllowed'
            # The file type is not in the specified list 'allowedfiletypes'
            console.log('Error: FileTypeNotAllowed')
    allowedfiletypes: ['image/jpeg', 'image/png', 'image/gif']
    maxfiles: 25
    maxfilesize: 20  # in MBs
    dragOver: ->
      console.log('dragOver')
      $(this).addClass('over')
    dragLeave: ->
      console.log('dragLeave')
      $(this).removeClass('over')
    ###
    docOver: ->
      console.log('docOver')
    docLeave: ->
      console.log('docLeave')
    ###
    drop: (event) ->
      console.log('drop', event)
      url = event.dataTransfer.getData('URL')
      if url
        console.log('url dropped', url)
      else if event.dataTransfer.files.length > 0
        console.log('file uploaded')
      else
        console.log('XXX unknown drop')
      $(this).removeClass('over')
    uploadStarted: (i, file, len) ->
      console.log('uploadStarted', i, file, len)
      createPreview(file)
      # a file began uploading
      # i = index => 0, 1, 2, 3, 4 etc
      # file is the actual file of the index
      # len = total files user dropped
    uploadFinished: (i, file, response, time) ->
      console.log('uploadFinished', i, file, response, time)
      # response is the data you got back from server in JSON format.
    progressUpdated: (i, file, progress) ->
      console.log('progressUpdated', i, file, progress)
      # this function is used for large files and updates intermittently
      # progress is the integer value of file being uploaded percentage to
      # completion
    globalProgressUpdated: (progress) ->
      # progress for all the files uploaded on the current instance
      # (percentage)
      # ex: $('#progress div').width(progress+"%");
    speedUpdated: (i, file, speed) ->
      # speed in kb/s
    rename: (name) ->
      # name in string format
      # must return alternate name as string
    ###
    beforeEach: (file) ->
      console.log('beforeEach', file)
      # file is a file object
      # return false to cancel upload
    beforeSend: (file, i, done) ->
      # file is a file object
      # i is the file index
      # call done() to start the upload
      done()
    afterAll: ->
      # runs after all files have been uploaded or otherwise dealt with
    ###


  createPreview = (file) ->
    img = $('<img>')
    img.width(100)
    # img.height(100)

    reader = new FileReader
    reader.onload = (e) -> img.attr('src', e.target.result)
    reader.readAsDataURL(file)

    img.appendTo('.grid')

#_.delay(f, 500)
