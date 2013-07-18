I set up a `.go` directory inside my checkout, which I use as a go workspace.
`.go/activate` contains:

    #!zsh
    export GOPATH=$(cd $(dirname $0); pwd)
    path+=$GOPATH/bin

It must be `source`d when you begin work on this project.
`.go/src/github.com/cabin/collate` is a soft link to the main checkout.

To get started:

    % go get          # install go dependencies
    % npm install     # install grunt and its dependencies
    % grunt bowerful  # install vendor web components

`grunt dev` will start a development server that automatically rebuilds
any changed files, including a LiveReload server.
