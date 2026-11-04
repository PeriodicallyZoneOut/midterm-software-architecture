package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type greetingResponse struct {
	Message string `json:"message"`
}

// Keep the database behind helloservice; the browser only calls the frontend.
func helloHandler(serviceURL string) http.HandlerFunc {
	client := &http.Client{
		Timeout: 5 * time.Second,
		CheckRedirect: func(_ *http.Request, _ []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		unavailable := func(status int) {
			w.WriteHeader(status)
			fmt.Fprintln(w, `{"error":"Could not get the greeting. Please try again."}`)
		}
		req, err := http.NewRequestWithContext(r.Context(), http.MethodGet,
			strings.TrimRight(serviceURL, "/")+"/hello", nil)
		if err != nil {
			unavailable(http.StatusServiceUnavailable)
			return
		}
		resp, err := client.Do(req)
		if err != nil {
			unavailable(http.StatusServiceUnavailable)
			return
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			unavailable(http.StatusBadGateway)
			return
		}
		body, err := io.ReadAll(io.LimitReader(resp.Body, 4097))
		var greeting greetingResponse
		if err != nil || len(body) > 4096 || json.Unmarshal(body, &greeting) != nil ||
			strings.TrimSpace(greeting.Message) == "" {
			unavailable(http.StatusBadGateway)
			return
		}
		json.NewEncoder(w).Encode(greeting)
	}
}
