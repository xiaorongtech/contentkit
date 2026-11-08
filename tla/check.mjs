import { check } from "tla-ts";
import { readFile } from "node:fs/promises";
const source = await readFile(new URL("./KeepAwake.tla", import.meta.url), "utf8");
const result = await check({ source, config: "INIT Init NEXT Next INVARIANT TypeOK" });
console.log("TypeOK:", result.status);
