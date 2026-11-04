package main

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHelloHandler(t *testing.T) {
	tests := []struct {
		name   string
		status int
		body   string
		want   int
	}{
		{"database greeting", 200, `{"message":"Hello world!"}`, 200},
		{"changed database greeting", 200, `{"message":"Changed in MariaDB"}`, 200},
		{"database unavailable", 503, `{"error":"private details"}`, 502},
		{"missing row", 404, `{"error":"missing"}`, 502},
		{"invalid JSON", 200, `<html>error</html>`, 502},
		{"missing message", 200, `{}`, 502},
		{"empty message", 200, `{"message":"  "}`, 502},
		{"oversized response", 200, `{"message":"` + strings.Repeat("x", 4096) + `"}`, 502},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if r.Method != http.MethodGet || r.URL.Path != "/hello" {
					t.Errorf("unexpected upstream request: %s %s", r.Method, r.URL.Path)
				}
				w.WriteHeader(tt.status)
				w.Write([]byte(tt.body))
			}))
			defer upstream.Close()
			response := httptest.NewRecorder()
			helloHandler(upstream.URL)(response, httptest.NewRequest(http.MethodGet, "/hello", nil))
			if response.Code != tt.want {
				t.Fatalf("status = %d, want %d; body = %s", response.Code, tt.want, response.Body)
			}
			if response.Header().Get("Cache-Control") != "no-store" {
				t.Error("greetings must not be cached")
			}
			if tt.want == http.StatusOK {
				var actual, expected greetingResponse
				if err := json.Unmarshal(response.Body.Bytes(), &actual); err != nil {
					t.Fatal(err)
				}
				json.Unmarshal([]byte(tt.body), &expected)
				if actual.Message != expected.Message {
					t.Errorf("message = %q, want %q", actual.Message, expected.Message)
				}
			} else if strings.Contains(response.Body.String(), "private details") {
				t.Error("upstream error details leaked")
			}
		})
	}
}

func TestHelloHandlerRespectsCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	r := httptest.NewRequest(http.MethodGet, "/hello", nil).WithContext(ctx)
	response := httptest.NewRecorder()
	helloHandler("http://127.0.0.1:1")(response, r)
	if response.Code != http.StatusServiceUnavailable {
		t.Fatalf("status = %d, want 503", response.Code)
	}
}

func TestHelloHandlerDoesNotFollowRedirects(t *testing.T) {
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/unexpected", http.StatusFound)
	}))
	defer upstream.Close()
	response := httptest.NewRecorder()
	helloHandler(upstream.URL)(response, httptest.NewRequest(http.MethodGet, "/hello", nil))
	if response.Code != http.StatusBadGateway {
		t.Fatalf("status = %d, want 502", response.Code)
	}
}
