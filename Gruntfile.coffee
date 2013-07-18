module.exports = (grunt) ->
  pkg = grunt.file.readJSON('package.json')
  spawn = require('child_process').spawn
  backendChild = null

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
          'git://github.com/trevex/golem_client.git': ''

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
        nospawn: true
      backend:
        files: ['**/*.go', 'templates/**/*']
        tasks: ['backend']
      coffee:
        files: ['<%= path.app %>/js/**/*.coffee']
        tasks: ['coffee']
      sass:
        files: ['<%= path.app %>/css/**/*.{sass,scss}']
        tasks: ['sass']

  # Build and run the go server, keeping track of the process and killing it
  # when run subsequently to support `grunt watch`. It's necessary to build and
  # run rather than use `go run` because we need to reliably signal the child
  # process, and `go run` is a layer between us and the actual go executable.
  # TODO: Relies on watch's nospawn option; could write a pid file instead.
  grunt.registerTask 'backend', 'Build and run the backend server', ->
    done = @async()
    buildAndRun = ->
      spawn('go', ['build'], cwd: __dirname).on 'exit', ->
        backendChild = spawn('./collate', [], cwd: __dirname)
        setTimeout(done, 100)
    if backendChild
      backendChild.on('exit', buildAndRun)
      backendChild.kill()
    else
      buildAndRun()

  # Load tasks from all required grunt plugins.
  for dep of pkg.devDependencies when dep.indexOf('grunt-') is 0
    grunt.loadNpmTasks(dep)

  grunt.registerTask('build', 'Build the client', ['coffee', 'sass'])
  grunt.registerTask('dev', 'Run a development server',
    ['backend', 'build', 'watch'])
