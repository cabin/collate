package backend

import (
	"code.google.com/p/gcfg"
	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"
	"html/template"
	"log"
	"net/http"
	"net/url"
)

// AppT provides a single place to keep application configuration, and acts as
// an http.Handler to allow a bit of "middleware".
type AppT struct {
	Config struct {
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
		[]byte(App.Config.Default.SecretKey), nil)
	App.Templates = parseTemplates(templateDir)
}

// getSession retrieves a pointer to the session object from its cookie.
func (app *AppT) getSession(r *http.Request) *sessions.Session {
	session, _ := app.CookieStore.Get(r, "session")
	return session
}

// render executes the given template filename and handles errors.
func (app *AppT) render(w http.ResponseWriter, tmpl string, data interface{}) {
	if err := app.Templates[tmpl].Execute(w, data); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

// url looks up a url in the app's router.
func (app *AppT) url(name string, args ...string) *url.URL {
	url, err := app.Router.Get(name).URL(args...)
	if err != nil {
		log.Fatal(err)
	}
	return url
}

// ServeHTTP implements the http.Handler interface.
func (app *AppT) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	app.Router.ServeHTTP(w, r)
}
