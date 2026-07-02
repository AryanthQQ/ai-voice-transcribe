import fs from "fs";
import { detectPhoneNumbers } from "../src/lib/analyzer";

const t1 = "n i n e i g h t o n e s e v e n t w o"; // missing one 'e'
const t2 = "n i n e e i g h t o n e s e v e n t w o";

console.log("Typo (nineight):", detectPhoneNumbers(t1, []).found);
console.log("Correct (nineeight):", detectPhoneNumbers(t2, []).found);
