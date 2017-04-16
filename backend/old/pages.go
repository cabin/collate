package backend

import (
	"html/template"
	"net/http"
)

var (
	indexTmpl = compileTemplate("index.html")
)

// http://stackoverflow.com/a/9587616/17052
// https://gist.github.com/traviscline/5562522
func compileTemplate(name string) *template.Template {
	return template.Must(template.ParseFiles(
		"templates/base.html", "templates/"+name))
}

func IndexHandler(w http.ResponseWriter, r *http.Request) {
	if err := indexTmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
