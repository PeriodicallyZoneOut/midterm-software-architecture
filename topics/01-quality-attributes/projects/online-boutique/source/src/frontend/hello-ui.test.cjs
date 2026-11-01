const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

function setup(fetch) {
  const button = {
    dataset: { url: "/demo/hello" }, disabled: false, textContent: "Get Hello",
    addEventListener(_name, handler) { this.click = handler; },
  };
  const message = { textContent: "" };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "static/js/hello.js"), "utf8"), {
    document: { getElementById: (id) => id === "get-hello" ? button : message },
    fetch, AbortController, setTimeout, clearTimeout,
  });
  return { button, message };
}

test("button fetches through the frontend base URL and displays returned text", async () => {
  const { button, message } = setup(async (url, options) => {
    assert.equal(url, "/demo/hello");
    assert.equal(options.cache, "no-store");
    return { ok: true, json: async () => ({ message: "Changed in MariaDB <b>hello</b>" }) };
  });
  const pending = button.click();
  assert.equal(button.disabled, true);
  await pending;
  assert.equal(message.textContent, "Changed in MariaDB <b>hello</b>");
  assert.equal(button.disabled, false);
  assert.equal(button.textContent, "Get Hello");
});

for (const scenario of ["network", "server", "invalid response"]) {
  test(`${scenario} failure shows a retry message and re-enables the button`, async () => {
    const { button, message } = setup(async () => {
      if (scenario === "network") throw new Error("offline");
      return { ok: scenario !== "server", json: async () => ({ message: null }) };
    });
    await button.click();
    assert.equal(message.textContent, "Could not get the greeting. Please try again.");
    assert.equal(button.disabled, false);
  });
}
