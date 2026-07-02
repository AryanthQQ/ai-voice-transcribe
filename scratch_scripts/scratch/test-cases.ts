import fs from "fs";
import { detectPhoneNumbers } from "../src/lib/analyzer";

const tests = [
  "nineighttwentyeighttwofour",
  "n i n e e i g h t t w e n t y e i g h t t w o f o u r",
  "n i n e e i g h t o n e s e v e n t w o",
  "nineeightoneseventwo",
  "nine eight one seven two"
];

for (const t of tests) {
  console.log(`Test: "${t}" -> found:`, detectPhoneNumbers(t, []).found);
}
