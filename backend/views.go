package backend

import (
	"fmt"
	"net/http"
)

func init() {
	App.Router.HandleFunc("/", indexHandler).
		Methods("GET").Name("index")
	App.Router.HandleFunc("/auth/login", loginHandler).
		Methods("GET").Name("login")
	App.Router.HandleFunc("/auth/login", loginHandler).
		Methods("POST")
	App.Router.HandleFunc("/auth/logout", logoutHandler).
		Methods("GET").Name("logout")
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	App.render(w, "index.html", nil)
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Print("%v %v\n", r.Method, r)

	if r.Method == "POST" {
		session := App.getSession(r)
		session.Values["username"] = "zakj"
		session.AddFlash("Logged in.")
		session.Save(r, w)
		http.Redirect(w, r, App.url("index").String(), http.StatusFound)
		return
	}
	App.render(w, "login.html", nil)
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
	session := App.getSession(r)
	delete(session.Values, "username")
	session.AddFlash("Logged out.")
	session.Save(r, w)
	http.Redirect(w, r, App.url("index").String(), http.StatusFound)
}
