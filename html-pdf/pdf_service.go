package main

import (
	"fmt"
	// "io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse form data
	err := r.ParseMultipartForm(10 << 20) // 10 MB max
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	htmlContent := r.FormValue("html")
	if htmlContent == "" {
		http.Error(w, "No HTML content provided", http.StatusBadRequest)
		return
	}

	// Create temp files
	tmpDir := os.TempDir()
	htmlFile := filepath.Join(tmpDir, "input.html")
	pdfFile := filepath.Join(tmpDir, "output.pdf")

	// Write HTML to temp file
	err = os.WriteFile(htmlFile, []byte(htmlContent), 0644)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer os.Remove(htmlFile)

	// Convert HTML to PDF using wkhtmltopdf
	cmd := exec.Command("wkhtmltopdf", "--quiet", htmlFile, pdfFile)
	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf("PDF conversion failed: %v", err), http.StatusInternalServerError)
		return
	}
	defer os.Remove(pdfFile)

	// Read PDF and send response
	pdfData, err := os.ReadFile(pdfFile)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Length", fmt.Sprintf("%d", len(pdfData)))
	w.Write(pdfData)
	
	log.Println("✅ Converted HTML to PDF")
}

func main() {
	http.HandleFunc("/convert", convertHandler)
	port := "8080"
	if p := os.Getenv("PORT"); p != "" {
		port = p
	}
	log.Printf("📄 PDF Service running on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}