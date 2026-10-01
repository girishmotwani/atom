// Command goextract walks a directory of Go source and reports, for every file,
// the symbols that file declares and the symbols it refers to.
//
// It parses with go/parser at syntax level only. It does not type-check, does
// not resolve imports, and does not need the code to build -- snapshots of a
// repository subtree usually will not build on their own, so anything stricter
// would fail on most inputs.
//
// The consequence worth stating plainly: references are matched by name, not by
// resolved identity. Two unrelated types that both declare a method named
// `Close` are indistinguishable here. This is a navigational aid, not a
// semantically precise call graph.
//
// Output is one JSON object per line, so a large repository can be streamed
// rather than held in memory:
//
//	{"file":"pkg/a/b.go","package":"a","defs":[...],"refs":[...]}
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// fileRecord is what we emit for a single Go source file.
type fileRecord struct {
	File    string   `json:"file"`    // repo-relative, forward slashes
	Package string   `json:"package"` // declared package name
	Defs    []string `json:"defs"`    // symbols declared here
	Refs    []string `json:"refs"`    // symbols mentioned here
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: goextract <root-directory>")
		os.Exit(2)
	}
	root := os.Args[1]

	encoder := json.NewEncoder(os.Stdout)
	walkErr := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			// An unreadable directory should not abort the whole index.
			return nil
		}
		if info.IsDir() {
			if shouldSkipDirectory(info.Name()) {
				return filepath.SkipDir
			}
			return nil
		}
		if !strings.HasSuffix(path, ".go") {
			return nil
		}
		record, parseErr := extractFile(root, path)
		if parseErr != nil {
			// Generated or partial files may not parse. Skipping one file is
			// far better than failing the run, but we say so on stderr.
			fmt.Fprintf(os.Stderr, "skip %s: %v\n", path, parseErr)
			return nil
		}
		return encoder.Encode(record)
	})
	if walkErr != nil {
		fmt.Fprintf(os.Stderr, "walk failed: %v\n", walkErr)
		os.Exit(1)
	}
}

// shouldSkipDirectory reports directories that only add noise to the index.
func shouldSkipDirectory(name string) bool {
	switch name {
	case ".git", "vendor", "node_modules", "testdata", ".atom-index":
		return true
	}
	return false
}

// extractFile parses one Go file into a fileRecord.
func extractFile(root string, path string) (fileRecord, error) {
	source, err := os.ReadFile(path)
	if err != nil {
		return fileRecord{}, err
	}

	fileSet := token.NewFileSet()
	// SkipObjectResolution: we do our own name collection and do not need
	// go/parser to build its (deprecated) object graph.
	syntaxTree, err := parser.ParseFile(fileSet, path, source, parser.SkipObjectResolution)
	if err != nil {
		return fileRecord{}, err
	}

	relative, err := filepath.Rel(root, path)
	if err != nil {
		relative = path
	}

	defs := newStringSet()
	refs := newStringSet()
	collectDeclarations(syntaxTree, defs)
	collectReferences(syntaxTree, refs)

	// A symbol declared in this file is not also a "reference" from it. Keeping
	// the two disjoint is what lets `who-uses` mean "used somewhere else".
	for name := range defs.items {
		delete(refs.items, name)
	}

	return fileRecord{
		File:    filepath.ToSlash(relative),
		Package: syntaxTree.Name.Name,
		Defs:    defs.sorted(),
		Refs:    refs.sorted(),
	}, nil
}

// collectDeclarations records every symbol the file declares.
//
// Methods are recorded twice: bare (`Close`) and receiver-qualified
// (`Server.Close`). The bare form keeps lookups easy when the caller only knows
// a method name; the qualified form lets a caller disambiguate when they know
// the type.
func collectDeclarations(syntaxTree *ast.File, defs *stringSet) {
	for _, declaration := range syntaxTree.Decls {
		switch typed := declaration.(type) {

		case *ast.FuncDecl:
			defs.add(typed.Name.Name)
			if receiverType := receiverTypeName(typed); receiverType != "" {
				defs.add(receiverType + "." + typed.Name.Name)
			}

		case *ast.GenDecl:
			for _, spec := range typed.Specs {
				switch specTyped := spec.(type) {

				case *ast.TypeSpec:
					defs.add(specTyped.Name.Name)
					// Interface method names are part of the contract other
					// packages code against, so they are worth indexing.
					if interfaceType, ok := specTyped.Type.(*ast.InterfaceType); ok {
						for _, method := range interfaceType.Methods.List {
							for _, methodName := range method.Names {
								defs.add(methodName.Name)
								defs.add(specTyped.Name.Name + "." + methodName.Name)
							}
						}
					}
					// Struct field names are indexed qualified only. Bare field
					// names like `Name` or `ID` are far too common to be useful
					// on their own and would swamp the index.
					if structType, ok := specTyped.Type.(*ast.StructType); ok {
						for _, field := range structType.Fields.List {
							for _, fieldName := range field.Names {
								defs.add(specTyped.Name.Name + "." + fieldName.Name)
							}
						}
					}

				case *ast.ValueSpec:
					for _, name := range specTyped.Names {
						defs.add(name.Name)
					}
				}
			}
		}
	}
}

// receiverTypeName returns the bare type name a method hangs off, stripping any
// pointer or generic decoration. It returns "" for plain functions.
func receiverTypeName(function *ast.FuncDecl) string {
	if function.Recv == nil || len(function.Recv.List) == 0 {
		return ""
	}
	return baseTypeName(function.Recv.List[0].Type)
}

// baseTypeName unwraps *T, T[K], and *T[K] down to T.
func baseTypeName(expression ast.Expr) string {
	switch typed := expression.(type) {
	case *ast.Ident:
		return typed.Name
	case *ast.StarExpr:
		return baseTypeName(typed.X)
	case *ast.IndexExpr: // generic receiver, e.g. Cache[K]
		return baseTypeName(typed.X)
	case *ast.IndexListExpr: // generic receiver with several parameters
		return baseTypeName(typed.X)
	}
	return ""
}

// collectReferences records every symbol the file mentions.
//
// Both halves of a qualified reference are kept: `storage.NewClient` yields
// `NewClient` and `storage.NewClient`. The caller usually knows one or the
// other, rarely both.
func collectReferences(syntaxTree *ast.File, refs *stringSet) {
	ast.Inspect(syntaxTree, func(node ast.Node) bool {
		switch typed := node.(type) {

		case *ast.SelectorExpr:
			refs.add(typed.Sel.Name)
			if qualifier, ok := typed.X.(*ast.Ident); ok {
				refs.add(qualifier.Name + "." + typed.Sel.Name)
			}

		case *ast.Ident:
			if isInterestingIdentifier(typed.Name) {
				refs.add(typed.Name)
			}
		}
		return true
	})
}

// isInterestingIdentifier filters out names that would match nearly every file
// and therefore carry no navigational signal.
func isInterestingIdentifier(name string) bool {
	if len(name) < 3 {
		return false
	}
	switch name {
	case "err", "nil", "true", "false", "iota", "len", "cap", "make", "new",
		"append", "copy", "delete", "panic", "recover", "print", "println",
		"string", "int", "int8", "int16", "int32", "int64", "uint", "uint8",
		"uint16", "uint32", "uint64", "float32", "float64", "bool", "byte",
		"rune", "error", "any", "ctx", "val":
		return false
	}
	return true
}

// stringSet is a small ordered-on-demand set, used to dedupe symbol names.
type stringSet struct {
	items map[string]struct{}
}

func newStringSet() *stringSet {
	return &stringSet{items: make(map[string]struct{})}
}

func (set *stringSet) add(name string) {
	if name == "" || name == "_" {
		return
	}
	set.items[name] = struct{}{}
}

func (set *stringSet) sorted() []string {
	names := make([]string, 0, len(set.items))
	for name := range set.items {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}
