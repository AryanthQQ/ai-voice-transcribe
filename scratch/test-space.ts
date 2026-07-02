import fs from "fs";
import { detectPhoneNumbers } from "../src/lib/analyzer";

console.log(detectPhoneNumbers("n i n e e i g h t o n e s e v e n t w o ", []).found);
