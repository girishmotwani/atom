package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

func main() {
	root, err := os.MkdirTemp("", "review-snapshot-fingerprint-")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	defer os.RemoveAll(root)

	selectedPath := filepath.Join(root, "changed.go")
	selectedBefore := []byte("package review\n")
	if err := os.WriteFile(selectedPath, selectedBefore, 0o600); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	unrelatedPath := filepath.Join(root, "unrelated.txt")
	for index := 0; index < 1000; index++ {
		path := filepath.Join(root, fmt.Sprintf("unrelated-%04d.txt", index))
		if err := os.WriteFile(path, []byte("unrelated fixture content\n"), 0o600); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	if err := os.WriteFile(unrelatedPath, []byte("unrelated original\n"), 0o600); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}

	selectedPaths := []string{"changed.go"}
	beforeReads := []string{}
	beforeIdentity, beforeBytes, err := identity(root, selectedPaths, &beforeReads)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	selectedChanged := []byte("package changed\n")
	if err := os.WriteFile(selectedPath, selectedChanged, 0o600); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	afterReads := []string{}
	afterIdentity, afterBytes, err := identity(root, selectedPaths, &afterReads)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	selectedMutationDetected := beforeIdentity != afterIdentity
	selectedReadsOnly := len(beforeReads) == 1 && len(afterReads) == 1 &&
		beforeReads[0] == "changed.go" && afterReads[0] == "changed.go"

	if err := os.WriteFile(selectedPath, selectedBefore, 0o600); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	unrelatedBeforeReads := []string{}
	unrelatedBeforeIdentity, _, err := identity(root, selectedPaths, &unrelatedBeforeReads)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if err := os.WriteFile(unrelatedPath, []byte("unrelated changed\n"), 0o600); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	unrelatedAfterReads := []string{}
	unrelatedAfterIdentity, _, err := identity(root, selectedPaths, &unrelatedAfterReads)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	unrelatedIgnored := unrelatedBeforeIdentity == unrelatedAfterIdentity
	unrelatedUntouched := len(unrelatedBeforeReads) == 1 && len(unrelatedAfterReads) == 1 &&
		unrelatedBeforeReads[0] == "changed.go" && unrelatedAfterReads[0] == "changed.go"

	fmt.Printf("fixture_files=1002 selected_paths=1\n")
	fmt.Printf("selected_mutation_detected=%t selected_reads=%d bytes_read=%d\n",
		selectedMutationDetected, len(beforeReads)+len(afterReads), beforeBytes+afterBytes)
	fmt.Printf("unrelated_mutation_ignored=%t unrelated_files_opened=%t scoped_reads=%d\n",
		unrelatedIgnored, !unrelatedUntouched, len(unrelatedBeforeReads)+len(unrelatedAfterReads))
	if !selectedMutationDetected || !selectedReadsOnly || !unrelatedIgnored || !unrelatedUntouched {
		os.Exit(1)
	}
}

func identity(root string, selectedPaths []string, reads *[]string) (string, int, error) {
	paths := append([]string(nil), selectedPaths...)
	sort.Strings(paths)
	digest := sha256.New()
	totalBytes := 0
	for _, relativePath := range paths {
		content, err := os.ReadFile(filepath.Join(root, relativePath))
		if err != nil {
			return "", totalBytes, err
		}
		*reads = append(*reads, relativePath)
		totalBytes += len(content)
		digest.Write([]byte(relativePath))
		digest.Write([]byte{0})
		digest.Write(content)
	}
	return hex.EncodeToString(digest.Sum(nil)), totalBytes, nil
}
