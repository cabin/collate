package main

import (
	"flag"
	"github.com/cabin/collate/backend"
	"log"
	"net/http"
)

var (
	address     = flag.String("address", ":4321", "network address")
	devServer   = flag.Bool("dev", false, "serve static assets")
	config      = flag.String("config", "settings.gcfg", "configuration file")
	templateDir = flag.String("templates", "templates", "template directory")
)

func main() {
	flag.Parse()
	if *devServer {
		http.Handle("/static/", http.StripPrefix("/static/",
			http.FileServer(http.Dir("app"))))
	}
	backend.InitApp(config, templateDir)
	http.Handle("/", backend.App)
	log.Fatal(http.ListenAndServe(*address, nil))
}
