import { execFileSync } from "node:child_process";
import { cpSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const output = path.join(root, "dist");
rmSync(output, { recursive: true, force: true });
mkdirSync(output, { recursive: true });

for (const app of ["main", "products", "cart"]) {
  execFileSync(process.execPath, [
    path.join(root, "node_modules/webpack-cli/bin/cli.js"),
    "build", "--mode", "production",
    "--env", "PRODUCTS_HOST=/products",
    "--env", "CART_HOST=/cart",
    "--env", "DOCKER_BUILD=true",
  ], { cwd: path.join(root, app), stdio: "inherit" });

  const destination = app === "main" ? output : path.join(output, app);
  mkdirSync(destination, { recursive: true });
  cpSync(path.join(root, app, "dist"), destination, { recursive: true });
  for (const name of readdirSync(path.join(root, app, "public"))) {
    if (name !== "index.html") {
      cpSync(path.join(root, app, "public", name), path.join(destination, name), { recursive: true });
    }
  }
}

const index = path.join(output, "index.html");
const { readFileSync, writeFileSync } = await import("node:fs");
writeFileSync(index, readFileSync(index, "utf8").replaceAll("%PUBLIC_URL%", ""));
