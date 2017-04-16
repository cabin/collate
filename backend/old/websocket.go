package backend

import (
	"fmt"
	"github.com/trevex/golem"
)

func init() {
	fmt.Printf("websocket init\n")
}

var (
	roomManager    = golem.NewRoomManager()
	connectionData = map[*golem.Connection]*ConnectionData{}
)

type Hello struct {
	From string `json:"from"`
}

type Answer struct {
	Msg      string `json:"msg"`
	Username string `json:"username"`
}

type ConnectionData struct {
	username string
}

func getData(conn *golem.Connection) *ConnectionData {
	cd, ok := connectionData[conn]
	if !ok {
		connectionData[conn] = &ConnectionData{}
		cd = connectionData[conn]
	}
	return cd
}

func hello(conn *golem.Connection, data *Hello) {
	cd := getData(conn)
	fmt.Printf("join from %v\n", cd)
	conn.Emit("answer", &Answer{"Thanks, " + data.From + "! You da bess.", cd.username})
}

func NewRouter() *golem.Router {
	router := golem.NewRouter()

	router.On("hello", hello)

	router.OnClose(func(conn *golem.Connection) {
		// TODO: emit leave notification
		roomManager.LeaveAll(conn)
		delete(connectionData, conn)
	})

	return router
}
