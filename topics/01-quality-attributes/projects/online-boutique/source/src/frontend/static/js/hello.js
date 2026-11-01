(() => {
  const button = document.getElementById("get-hello");
  const message = document.getElementById("hello-message");
  if (!button || !message) return;

  button.addEventListener("click", async () => {
    button.disabled = true;
    button.textContent = "Loading…";
    message.textContent = "Getting your greeting…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(button.dataset.url, {
        signal: controller.signal,
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) throw new Error("Greeting request failed");
      const result = await response.json();
      if (typeof result.message !== "string" || !result.message.trim()) {
        throw new Error("Invalid greeting response");
      }
      message.textContent = result.message;
    } catch {
      message.textContent = "Could not get the greeting. Please try again.";
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
      button.textContent = "Get Hello";
    }
  });
})();
