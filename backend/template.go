package backend

import (
	"html/template"
	"log"
	"path/filepath"
)

// parseTemplates compiles all templates in the given templateDir, along with
// the base template, and assigns them to a map.
func parseTemplates(templateDir *string) map[string]*template.Template {
	baseName := "base.html"
	baseTemplate := filepath.Join(*templateDir, baseName)
	templates := make(map[string]*template.Template)
	// TODO: This loads all templates at first runtime, but doesn't ensure that
	// some view isn't using a template that doesn't exist. Maybe some kind of
	// map of handlers to their template files?
	files, err := filepath.Glob(filepath.Join(*templateDir, "*.html"))
	if err != nil {
		log.Fatal(err)
	}
	funcMap := template.FuncMap{
		"username": func() string {
			return "username"
		},
	}
	for _, filename := range files {
		if filename == baseTemplate {
			continue
		}
		name := filepath.Base(filename)
		tmpl, err := template.New(baseName).
			Funcs(funcMap).
			ParseFiles(baseTemplate, filename)
		if err != nil {
			log.Fatal(err)
		}
		templates[name] = tmpl
	}
	return templates
}
