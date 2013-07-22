package backend

import (
	"net/http"
)

func init() {
	App.Router.HandleFunc("/", IndexHandler).Methods("GET")
}

func IndexHandler(w http.ResponseWriter, r *http.Request) {
	if err := App.Templates["index.html"].Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
