import { detectPhoneNumbers } from "../src/lib/analyzer";

const transcript = "n i n e e i g h t o n e s e v e n t w o";
const result = detectPhoneNumbers(transcript, []);
console.log(JSON.stringify(result, null, 2));
