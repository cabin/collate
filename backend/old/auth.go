package backend

import (
	//"github.com/gorilla/securecookie"
	"github.com/gorilla/context"
	"github.com/gorilla/sessions"
	"net/http"
)

var (
	loginTmpl = compileTemplate("login.html")
)


func LoginHandler(w http.ResponseWriter, r *http.Request) {
	if err := loginTmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	if sessionInterface, ok := context.GetOk(r, "session"); ok {
		session := sessionInterface.(sessions.Session)
		delete(session.Values, "username")
		session.Save(r, w)
	}
	http.Redirect(w, r, "/", http.StatusFound)
}
