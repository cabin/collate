package backend

import (
	"github.com/gorilla/sessions"
	"github.com/trevex/golem"
	"net/http"
)

func init() {
	router := golem.NewRouter()
	App.Router.HandleFunc("/ws", router.Handler())

	router.OnHandshake(validateSession)
	router.SetConnectionExtension(NewConnection)
	router.On("hello", hello)
	router.OnClose(func(conn *golem.Connection) {
		// TODO: emit leave notification
		roomManager.LeaveAll(conn)
	})
}

type Connection struct {
	*golem.Connection
	Session *sessions.Session
}

func NewConnection(conn *golem.Connection) *Connection {
	return &Connection{
		Connection: conn,
		Session:    App.getSession(lastWebsocketRequest),
	}
}

var (
	// lastWebsocketRequest is a hack to pass the current request to
	// NewConnection, in order to associate an HTTP session with a Golem
	// connection. TODO: patch Golem.
	lastWebsocketRequest *http.Request
	roomManager          = golem.NewRoomManager()
)

type Hello struct {
	From string `json:"from"`
}

type Answer struct {
	Msg      string `json:"msg"`
	Username string `json:"username"`
}

func validateSession(w http.ResponseWriter, r *http.Request) bool {
	session := App.getSession(r)
	_, ok := session.Values["username"]
	if ok || true { // XXX
		lastWebsocketRequest = r
		return true
	} else {
		return false
	}
}

func hello(conn *Connection, data *Hello) {
	un := conn.Session.Values["username"].(string)
	conn.Emit("answer", &Answer{
		"data.From: " + data.From + "; Session.username:",
		un,
	})
}
