import { readFileSync, writeFileSync } from "node:fs";

const apps = ["main", "products", "cart"];
const manifests = Object.fromEntries(apps.map(app => [app, JSON.parse(readFileSync(`${app}/package.json`, "utf8"))]));
const versions = Object.assign({}, ...apps.map(app => ({ ...manifests[app].dependencies, ...manifests[app].devDependencies })));
const runtime = {
  main: ["react", "react-dom", "react-router-dom", "@mui/material", "@mui/icons-material", "@emotion/react", "@emotion/styled", "uuid", "web-vitals"],
  products: ["react", "react-dom", "@mui/material", "@mui/icons-material", "@emotion/react", "@emotion/styled", "web-vitals"],
  cart: ["react", "react-dom", "react-router-dom", "@mui/material", "@mui/icons-material", "@emotion/react", "@emotion/styled", "zustand", "web-vitals"],
};
const tools = [
  "@babel/core", "@babel/preset-env", "@babel/preset-react", "@babel/preset-typescript",
  "@babel/plugin-transform-runtime", "babel-loader", "css-loader", "file-loader",
  "html-webpack-plugin", "dotenv-webpack", "ts-loader", "typescript", "webpack", "webpack-cli",
];
const pick = names => Object.fromEntries(names.map(name => {
  if (!versions[name]) throw new Error(`Missing version for required build dependency: ${name}`);
  return [name, versions[name]];
}));
for (const app of apps) {
  writeFileSync(`${app}/package.json`, JSON.stringify({
    name: app, version: manifests[app].version, private: true,
    dependencies: pick(runtime[app]), browserslist: manifests[app].browserslist,
  }, null, 2) + "\n");
}
writeFileSync("package.json", JSON.stringify({
  name: "micro-frontend-demo", version: "0.1.0", private: true,
  packageManager: "yarn@1.22.22", workspaces: apps,
  scripts: { "build:docker": "node scripts/build-docker.mjs" },
  devDependencies: { ...pick(tools), "style-loader": "^3.3.1" },
}, null, 2) + "\n");
writeFileSync("yarn.lock", readFileSync("yarn.lock", "utf8").replaceAll("https://registry.yarnpkg.com/", "https://registry.npmjs.org/"));
console.log(`Docker install: ${tools.length + 1} build tools and ${new Set(Object.values(runtime).flat()).size} runtime libraries, plus their transitive dependencies.`);
