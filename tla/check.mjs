import { check } from "tla-ts";
import { readFile } from "node:fs/promises";
const source = await readFile(new URL("./KeepAwake.tla", import.meta.url), "utf8");
for (const inv of ["TypeOK", "FailHasRetries"]) {
  const result = await check({ source, config: `INIT Init NEXT Next INVARIANT ${inv}` });
  console.log(inv + ":", result.status);
  if (result.violation?.trace) console.log("  trace:", JSON.stringify(result.violation.trace).slice(0, 600));
}
