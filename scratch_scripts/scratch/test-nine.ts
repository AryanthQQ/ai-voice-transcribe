import fs from "fs";
import { detectPhoneNumbers } from "../src/lib/analyzer";

const tests = [
  "onenintwoeightseven"
];

for (const t of tests) {
  console.log(`Test: "${t}" -> found:`, detectPhoneNumbers(t, []).found);
}
