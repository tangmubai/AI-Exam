import { cp, mkdir, readdir, rm } from "node:fs/promises";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const dist = join(root, "dist");

const siteFiles = [
  "_headers",
  "_redirects",
  "index.html",
  "practice.html",
  "styles.css",
  "app.js",
  "practice.js",
  "questions.js"
];

await mkdir(dist, { recursive: true });
for (const entry of await readdir(dist)) {
  await rm(join(dist, entry), { recursive: true, force: true });
}

for (const file of siteFiles) {
  await cp(join(root, file), join(dist, file));
}

for (const entry of await readdir(root, { withFileTypes: true })) {
  if (entry.isFile() && extname(entry.name).toLowerCase() === ".pdf") {
    await cp(join(root, entry.name), join(dist, entry.name));
  }
}

console.log(`Built static site in ${dist}`);
