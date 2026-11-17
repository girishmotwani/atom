// This disposable command measures setup mechanics, not real agent consent.
package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"fmt"
	"go/format"
	"os"
	"os/exec"
	"path/filepath"
	"reflect"
	"runtime"
	"sort"
	"strings"
	"time"
)

const question = "Can the existing Go module-initialization and Atom onboarding commands compose into a locally usable setup from a repository without `go.mod`, preserving pre-existing files and reporting empty-module validation honestly?"
const source = "package main\n\nimport \"fmt\"\n\nfunc greeting() string { return \"ready\" }\n\nfunc main() { fmt.Println(greeting()) }\n"
const sourceTest = "package main\n\nimport \"testing\"\n\nfunc TestGreeting(t *testing.T) {\n\tif greeting() != \"ready\" { t.Fatal(\"unexpected greeting\") }\n}\n"

var childEnvironment []string
var commandCount int
var timedOut bool

func main() {
	verdict, exitCode, root := "Inconclusive", 2, ""
	defer func() {
		if problem := recover(); problem != nil {
			emit(map[string]any{"event": "failure", "error": fmt.Sprint(problem)})
			if strings.HasPrefix(fmt.Sprint(problem), "Refuted:") {
				verdict, exitCode = "Refuted", 1
			}
		}
		if root != "" && !timedOut {
			if err := os.RemoveAll(root); err != nil {
				emit(map[string]any{"event": "cleanup-error", "path": root, "error": err.Error()})
				verdict, exitCode = "Inconclusive", 2
			} else {
				emit(map[string]any{"event": "cleanup", "path": root, "removed": true})
			}
		}
		if timedOut {
			emit(map[string]any{"event": "cleanup-deferred", "path": root, "reason": "process-tree cleanup is not proven"})
		}
		emit(map[string]any{"event": "verdict", "verdict": verdict, "commands": commandCount, "real_agent_consent_tested": false})
		os.Exit(exitCode)
	}()

	emit(map[string]any{"event": "question", "question": question, "platform": runtime.GOOS, "runtime": runtime.Version()})
	goExecutable, err := exec.LookPath("go")
	must(err)
	pythonExecutable, err := exec.LookPath("python")
	must(err)
	childEnvironment = os.Environ()
	paths := []string{filepath.Dir(goExecutable), filepath.Dir(pythonExecutable)}
	if runtime.GOOS == "windows" {
		paths = append(paths, filepath.Join(os.Getenv("SystemRoot"), "System32"))
	}
	for name, value := range map[string]string{
		"PATH":        strings.Join(paths, string(os.PathListSeparator)),
		"GOTOOLCHAIN": "local", "GOPROXY": "off", "GOSUMDB": "off",
	} {
		setChildEnvironment(name, value)
	}
	emit(map[string]any{"event": "environment", "go": goExecutable, "python": pythonExecutable,
		"child_path": strings.Join(paths, string(os.PathListSeparator)), "GOTOOLCHAIN": "local", "GOPROXY": "off", "GOSUMDB": "off"})
	run("", goExecutable, "version")
	run("", pythonExecutable, "--version")
	root, err = os.MkdirTemp("", "atom-v1-new-repo-setup-")
	must(err)

	for _, name := range []string{"module-only", "approved-cli", "existing-module", "declined"} {
		directory := filepath.Join(root, name)
		must(os.Mkdir(directory, 0700))
		write(directory, "README.md", "Existing user documentation.\n")
		emit(map[string]any{"event": "fixture", "case": name, "directory": directory})
		if name == "existing-module" {
			run(directory, goExecutable, "mod", "init", "example.com/"+name)
			write(directory, "main.go", source)
			write(directory, "main_test.go", sourceTest)
		}
		before := snapshot(directory)
		if name == "declined" {
			countBefore := commandCount
			require(reflect.DeepEqual(before, snapshot(directory)), "declined fixture content changed")
			require(commandCount == countBefore, "declined fixture launched a command")
			require(!exists(filepath.Join(directory, "go.mod")), "declined fixture gained go.mod")
			require(!exists(filepath.Join(directory, ".atom")), "declined fixture gained Atom state")
			emit(map[string]any{"event": "case-result", "case": name, "unchanged": true,
				"scope": "fixed harness decision only, not a real agent approval/refusal test"})
			continue
		}
		if name != "existing-module" {
			run(directory, goExecutable, "mod", "init", "example.com/"+name)
			if name == "approved-cli" {
				write(directory, "main.go", source)
				write(directory, "main_test.go", sourceTest)
			}
		}
		initOutput := run(directory, pythonExecutable, "-m", "atom.cli", "init")
		config := readObject(filepath.Join(directory, ".atom", "config.json"))
		require(config["module_path"] == "example.com/"+name, "module identity did not survive onboarding")
		after := snapshot(directory)
		for path, digest := range before {
			require(after[path] == digest, "onboarding changed existing file "+path)
		}
		require(exists(filepath.Join(directory, "go.mod")), "onboarding left no go.mod")
		baselinePath := filepath.Join(directory, ".atom", "baseline.json")
		baselineBytes, err := os.ReadFile(baselinePath)
		must(err)
		baseline := readObject(baselinePath)
		emit(map[string]any{"event": "baseline", "case": name, "raw_json": string(baselineBytes),
			"build_command": config["build_command"], "test_command": config["test_command"]})
		passed, isBoolean := baseline["passed"].(bool)
		require(isBoolean, "baseline omitted its boolean passed field")
		if name == "module-only" {
			if !passed {
				require(strings.Contains(initOutput, "FAIL"), "failing empty-module baseline was not disclosed")
			}
			emit(map[string]any{"event": "empty-module-limit", "passed": passed,
				"application_verified": false, "reason": "fixture contains no application or tests"})
		} else {
			require(passed, "tiny CLI baseline did not pass")
			require(config["build_command"] == "go build ./...", "unexpected recorded build command")
			require(config["test_command"] == "go test ./...", "unexpected recorded test command")
			gates, ok := baseline["gates"].([]any)
			require(ok, "baseline omitted gate results")
			for _, wanted := range []string{"build", "test"} {
				found := false
				for _, item := range gates {
					gate, ok := item.(map[string]any)
					require(ok, "invalid baseline gate")
					if gate["name"] == wanted {
						require(gate["status"] == "passed", wanted+" gate did not pass")
						found = true
					}
				}
				require(found, "missing "+wanted+" gate")
			}
		}
		created := make([]string, 0)
		for path := range after {
			if _, existed := before[path]; !existed {
				created = append(created, path)
			}
		}
		sort.Strings(created)
		if name == "existing-module" {
			run(directory, pythonExecutable, "-m", "atom.cli", "init")
			require(reflect.DeepEqual(after, snapshot(directory)), "matching repeat onboarding changed file contents")
		}
		emit(map[string]any{"event": "case-result", "case": name, "preserved_existing_files": true,
			"created_files": created, "baseline_passed": passed, "repeat_checked": name == "existing-module"})
	}
	verdict, exitCode = "Confirmed", 0
}

func run(directory, executable string, arguments ...string) string {
	commandCount++
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()
	command := exec.CommandContext(ctx, executable, arguments...)
	command.Dir = directory
	command.Env = childEnvironment
	command.WaitDelay = 5 * time.Second
	var stdout, stderr bytes.Buffer
	command.Stdout, command.Stderr = &stdout, &stderr
	err := command.Run()
	exitCode := -1
	if command.ProcessState != nil {
		exitCode = command.ProcessState.ExitCode()
	}
	emit(map[string]any{"event": "command", "number": commandCount, "executable": executable,
		"arguments": arguments, "cwd": directory, "exit_code": exitCode,
		"stdout": stdout.String(), "stderr": stderr.String(), "timed_out": errors.Is(ctx.Err(), context.DeadlineExceeded)})
	if ctx.Err() != nil {
		timedOut = true
		panic("Inconclusive: command timeout; child-tree cleanup not established")
	}
	if err != nil {
		panic(fmt.Sprintf("Inconclusive: command failed: %v", err))
	}
	return stdout.String()
}

func setChildEnvironment(name, value string) {
	filtered := make([]string, 0, len(childEnvironment)+1)
	for _, entry := range childEnvironment {
		key, _, _ := strings.Cut(entry, "=")
		if !strings.EqualFold(key, name) {
			filtered = append(filtered, entry)
		}
	}
	childEnvironment = append(filtered, name+"="+value)
}

func snapshot(directory string) map[string]string {
	files := make(map[string]string)
	must(filepath.WalkDir(directory, func(path string, entry os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !entry.IsDir() {
			data, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			relative, err := filepath.Rel(directory, path)
			if err != nil {
				return err
			}
			files[relative] = fmt.Sprintf("%x", sha256.Sum256(data))
		}
		return nil
	}))
	return files
}

func readObject(path string) map[string]any {
	data, err := os.ReadFile(path)
	must(err)
	var object map[string]any
	must(json.Unmarshal(data, &object))
	return object
}

func write(directory, name, content string) {
	data := []byte(content)
	if strings.HasSuffix(name, ".go") {
		formatted, err := format.Source(data)
		must(err)
		data = formatted
	}
	must(os.WriteFile(filepath.Join(directory, name), data, 0600))
}

func exists(path string) bool {
	_, err := os.Stat(path)
	if errors.Is(err, os.ErrNotExist) {
		return false
	}
	must(err)
	return true
}

func require(condition bool, message string) {
	if !condition {
		panic("Refuted: " + message)
	}
}

func must(err error) {
	if err != nil {
		panic("Inconclusive: " + err.Error())
	}
}

func emit(value any) {
	if err := json.NewEncoder(os.Stdout).Encode(value); err != nil {
		panic(err)
	}
}
