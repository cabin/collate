package backend

import (
	"code.google.com/p/gcfg"
	"github.com/gorilla/context"
	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"
	"html/template"
	"log"
	"net/http"
	"path/filepath"
)

// AppT provides a single place to keep application configuration, and acts as
// an http.Handler to allow a bit of "middleware".
type AppT struct {
	Config      struct {
		Default struct {
			SecretKey string
		}
	}
	CookieStore *sessions.CookieStore
	Router      *mux.Router
	Templates   map[string]*template.Template
}

// App is the singleton application instance; it must be initialized with a
// Router so that other files can set up handlers in init().
var App = &AppT{
	Router: mux.NewRouter(),
}

// InitApp configures App.
func InitApp(config *string, templateDir *string) {
	if err := gcfg.ReadFileInto(&App.Config, *config); err != nil {
		log.Fatal(err)
	}
	App.CookieStore = sessions.NewCookieStore(
		[]byte(App.Config.Default.SecretKey))
	App.Templates = parseTemplates(templateDir)
}

// parseTemplates compiles all templates in the given templateDir, along with
// the base template, and assigns them to a map.
func parseTemplates(templateDir *string) map[string]*template.Template {
	baseTemplate := filepath.Join(*templateDir, "base.html")
	templates := make(map[string]*template.Template)
	// TODO: This loads all templates at first runtime, but doesn't ensure that
	// some view isn't using a template that doesn't exist. Maybe some kind of
	// map of handlers to their template files?
	files, err := filepath.Glob(filepath.Join(*templateDir, "*.html"))
	if err != nil {
		log.Fatal(err)
	}
	for _, filename := range files {
		if filename == baseTemplate {
			continue
		}
		templates[filepath.Base(filename)] = template.Must(template.ParseFiles(
			baseTemplate, filename))
	}
	return templates
}

// ServeHTTP implements the http.Handler interface.
func (app *AppT) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	session, _ := App.CookieStore.Get(r, "session")
	context.Set(r, "session", session)
	app.Router.ServeHTTP(w, r)
}
