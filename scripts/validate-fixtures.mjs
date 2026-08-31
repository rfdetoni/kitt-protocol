import { readFileSync } from "node:fs";

const fixtures = [
  "fixtures/v1/assistant-ask-request.json",
  "fixtures/v1/assistant-ask-response.json",
  "fixtures/v1/memory-recall-request.json",
  "fixtures/v1/memory-recall-response.json",
  "fixtures/v1/hud-event.json",
  "fixtures/v1/error.json",
];

function assertEnvelope(value) {
  if (!value || typeof value !== "object") throw new Error("not an object");
  const allowed = new Set(["version", "id", "kind", "correlation_id", "payload"]);
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) throw new Error(`unknown envelope field ${key}`);
  }
  if (value.version !== 1) throw new Error("bad version");
  if (typeof value.id !== "string" || !value.id) throw new Error("bad id");
  if (typeof value.kind !== "string" || !value.kind) throw new Error("bad kind");
  if (!Object.prototype.hasOwnProperty.call(value, "payload")) throw new Error("missing payload");
}

for (const file of fixtures) {
  const value = JSON.parse(readFileSync(file, "utf8"));
  if (file.endsWith("-request.json") && Object.hasOwn(value, "token")) {
    if (Object.keys(value).sort().join(",") !== "envelope,token") {
      throw new Error(`${file}: bad authenticated frame`);
    }
    if (typeof value.token !== "string" || !value.token) throw new Error(`${file}: bad token`);
    assertEnvelope(value.envelope);
  } else {
    assertEnvelope(value);
  }
}
console.log(`validated ${fixtures.length} protocol fixtures`);
