module.exports = (grunt) ->
  pkg = grunt.file.readJSON('package.json')
  fs = require('fs')
  path = require('path')
  spawn = require('child_process').spawn

  grunt.initConfig
    pkg: pkg
    path:
      app: 'app'
      build: 'app/build'
      components: 'app/bower_components'

    bowerful:
      dist:
        store: '<%= path.components %>'
        packages:
          'angular-1.1.x': '1.1.5'
          'bourbon': '3.1.6'
          'normalize-css': '2.1.2'
          'https://github.com/trevex/golem_client.git': ''

    coffee:
      build:
        expand: true
        cwd: '<%= path.app %>'
        src: 'js/**/*.coffee'
        dest: '<%= path.build %>'
        ext: '.js'
    sass:
      build:
        expand: true
        cwd: '<%= path.app %>'
        src: ['css/**/*.{sass,scss}', '!css/**/_*']
        dest: '<%= path.build %>'
        ext: '.css'
      options:
        loadPath: '<%= path.components %>'

    watch:
      options:
        livereload: 35739
      backend:
        files: ['**/*.go', 'templates/**/*']
        tasks: ['backend']
      coffee:
        files: ['<%= path.app %>/js/**/*.coffee']
        tasks: ['coffee']
      sass:
        files: ['<%= path.app %>/css/**/*.{sass,scss}']
        tasks: ['sass']

    # TODO: dist; use grunt-ngmin to handle DI on angular files

  # Spawn a child process and record its pid in a file. If the pid file exists,
  # kill the listed pid before spawning. On exit, clean up the pid file.
  spawnWithPid = ->
    pidFile = path.join(__dirname, 'backend.pid')
    pid = fs.existsSync(pidFile) and fs.readFileSync(pidFile).toString()
    if pid
      try
        process.kill(pid)
      catch e
        # ignore
    child = spawn.apply(null, arguments).on('exit', -> fs.unlink(pidFile))
    fs.writeFileSync(pidFile, child.pid)
    return child

  # Build and run the go backend, keeping track of the process and killing it
  # when run subsequently to support `grunt watch`. It's necessary to build and
  # run rather than use `go run` in order to reliably signal the child process
  # (`go run` is a layer between us and the actual go executable).
  grunt.registerTask 'backend', 'Build and run the backend server', ->
    done = @async()
    # Ensure we're always running from the appropriate directory and can see
    # all process output.
    spawnOpts = cwd: __dirname, stdio: 'inherit'
    spawnWithPid('go', ['build'], spawnOpts).on 'exit', (code, signal) ->
      if code isnt 0
        grunt.warn('\x07build failed')
        return done()
      spawnWithPid('./collate', ['-dev'], spawnOpts)
      # Allow time to spin up before triggering live reload.
      setTimeout(done, 100)

  # Load tasks from all required grunt plugins.
  for dep of pkg.devDependencies when dep.indexOf('grunt-') is 0
    grunt.loadNpmTasks(dep)

  grunt.registerTask('build', 'Build the client', ['coffee', 'sass'])
  grunt.registerTask('dev', 'Run a development server',
    ['backend', 'build', 'watch'])
