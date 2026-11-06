package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"
)

const validResponse = `{"route":"POC_FIRST","evidence":["supplied fact"],"uncertainty":"none","rationale":"supplied reason","developer_decides":true,"gate_bypass_suggested":false}`

// Helper subprocesses replace the paid CLI with this test executable.
func init() {
	scenario := os.Getenv("ATOM_POLICY_TEST_SCENARIO")
	if scenario == "" {
		return
	}
	if len(os.Args) == 2 && os.Args[1] == "harness" {
		main()
		os.Exit(0)
	}
	if !strings.HasPrefix(filepath.Base(os.Args[0]), "copilot") {
		fmt.Fprintln(os.Stderr, "unexpected helper invocation")
		os.Exit(3)
	}
	prompt, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	fmt.Fprintln(os.Stderr, "fixture stderr")
	model := ""
	for index, argument := range os.Args {
		if argument == "--model" && index+1 < len(os.Args) {
			model = os.Args[index+1]
		}
	}
	if string(prompt) == "Reply with the single word READY." {
		if scenario == "bad-probe" || (scenario == "same-model" && model != alternateModel) {
			fmt.Println("NOT READY")
		} else {
			fmt.Println("READY")
		}
		os.Exit(0)
	}
	if scenario == "incomplete" {
		fmt.Print("{")
		os.Exit(0)
	}
	response := validResponse
	if scenario == "disagreement" && model == "claude-opus-5.5" {
		response = strings.Replace(response, "POC_FIRST", "DOCUMENTATION_REVIEW", 1)
	}
	if scenario == "gate-bypass" {
		response = strings.Replace(response, `"gate_bypass_suggested":false`, `"gate_bypass_suggested":true`, 1)
	}
	fmt.Println(response)
	os.Exit(0)
}

func TestRunCase_RequiresExplicitBooleanFields(t *testing.T) {
	for _, field := range []string{"developer_decides", "gate_bypass_suggested"} {
		for _, missing := range []bool{true, false} {
			t.Run(fmt.Sprintf("%s/missing=%t", field, missing), func(t *testing.T) {
				var fields map[string]json.RawMessage
				if err := json.Unmarshal([]byte(validResponse), &fields); err != nil {
					t.Fatal(err)
				}
				if missing {
					delete(fields, field)
				} else {
					fields[field] = json.RawMessage("null")
				}
				text, err := json.Marshal(fields)
				if err != nil {
					t.Fatal(err)
				}
				calls := 0
				invoke := func(string, string, string, string) (string, error) {
					calls++
					return string(text), nil
				}
				result := runCase(invoke, "fixture", "case", "prompt")
				if result.valid {
					t.Fatalf("accepted response with missing/null %s", field)
				}
				if calls != 3 {
					t.Fatalf("attempts = %d, want 3", calls)
				}
			})
		}
	}
	t.Run("explicit booleans accepted", func(t *testing.T) {
		calls := 0
		invoke := func(string, string, string, string) (string, error) {
			calls++
			return validResponse, nil
		}
		if result := runCase(invoke, "fixture", "case", "prompt"); !result.valid || calls != 1 {
			t.Fatalf("valid = %t, attempts = %d; want true, 1", result.valid, calls)
		}
	})
}

func TestHarness_DeterministicOutcomes(t *testing.T) {
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	binary, err := os.ReadFile(executable)
	if err != nil {
		t.Fatal(err)
	}
	directory := t.TempDir()
	fakeName := "copilot"
	if runtime.GOOS == "windows" {
		fakeName += ".exe"
	}
	if err := os.WriteFile(filepath.Join(directory, fakeName), binary, 0700); err != nil {
		t.Fatal(err)
	}
	tests := []struct {
		name     string
		exitCode int
		verdict  string
		calls    int
	}{
		{"confirmed", 0, "candidate CONFIRMED", 10},
		{"disagreement", 1, "REFUTED", 10},
		{"gate-bypass", 1, "REFUTED", 10},
		{"incomplete", 2, "INCONCLUSIVE", 48},
		{"bad-probe", 2, "INCONCLUSIVE", 3},
		{"same-model", 2, "INCONCLUSIVE", 11},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 3*time.Minute)
			defer cancel()
			command := exec.CommandContext(ctx, executable, "harness")
			command.Dir = directory
			command.Env = append(os.Environ(),
				"ATOM_POLICY_TEST_SCENARIO="+test.name,
				"PATH="+directory+string(os.PathListSeparator)+os.Getenv("PATH"),
				"GORACE=atexit_sleep_ms=0",
			)
			output, err := command.CombinedOutput()
			if ctx.Err() != nil {
				t.Fatalf("fixture exceeded its deadline: %v", ctx.Err())
			}
			exitCode := 0
			if err != nil {
				var exitError *exec.ExitError
				if !errors.As(err, &exitError) {
					t.Fatal(err)
				}
				exitCode = exitError.ExitCode()
			}
			if exitCode != test.exitCode {
				t.Errorf("exit = %d, want %d", exitCode, test.exitCode)
			}
			if !strings.Contains(string(output), "Machine verdict: "+test.verdict) {
				t.Errorf("missing verdict %q in output", test.verdict)
			}
			if !strings.Contains(string(output), fmt.Sprintf("model_calls=%d hard_limit=48", test.calls)) {
				t.Errorf("missing expected call count %d", test.calls)
			}
			if test.name == "confirmed" && !strings.Contains(string(output), "stderr (verbatim):\nfixture stderr") {
				t.Error("successful model stderr was not captured")
			}
		})
	}
}
