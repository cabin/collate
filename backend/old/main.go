package backend

import (
	"code.google.com/p/gcfg"
	_ "database/sql"
	"fmt"
	"github.com/gorilla/context"
	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"
	_ "github.com/lib/pq"
	"log"
	"net/http"
)

type RoomRequest struct {
	Name string `json:"name"`
}

/*
func join(conn *golem.Connection, data *RoomRequest) {
	// TODO: auth
	fmt.Printf("joining %s\n", data.Name)
	cd := getData(conn)
	if cd.username == "" {
		cd.username = "nutbar"
	} else {
		fmt.Printf("oops %v", cd.username);
	}
	roomManager.Join(data.Name, conn)
}

func leave(conn *golem.Connection, data *RoomRequest) {
	roomManager.Leave(data.Name, conn)
	//roomManager.Emit(data.Name, "leave"
}
*/

type Config struct {
	Default struct {
		SecretKey string
	}
}

func middleware(wrapped http.HandlerFunc, requireAuth bool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// TODO add context type
		session, _ := store.Get(r, "session")
		context.Set(r, "session", session)
		// TODO auth
		_, ok := session.Values["username"]
		if requireAuth && !ok {
			w.WriteHeader(http.StatusForbidden)
			fmt.Fprintf(w, "403 Forbidden\n")
		} else {
			wrapped(w, r)
		}
	}
}

/*
func requireAuth(wrapped http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// XXX TODO auth
		// TODO use gorilla context to share login data?
	}
}
*/

var store *sessions.CookieStore

func main() {
	var cfg Config
	if err := gcfg.ReadFileInto(&cfg, "settings.gcfg"); err != nil {
		log.Fatal(err)
	}

	store = sessions.NewCookieStore([]byte(cfg.Default.SecretKey))

	r := mux.NewRouter()

	wsRouter := NewRouter()
	r.HandleFunc("/ws", wsRouter.Handler())

	r.HandleFunc("/", middleware(IndexHandler, false)).Methods("GET")
	r.HandleFunc("/auth/login", middleware(LoginHandler, false)).
		Methods("GET", "POST")
	r.HandleFunc("/auth/logout", middleware(LogoutHandler, false))

	// TODO: only in development
	http.Handle("/static/", http.StripPrefix("/static/",
		http.FileServer(http.Dir("app"))))

	http.Handle("/", r)
	log.Fatal(http.ListenAndServe(":4321", nil))
}
