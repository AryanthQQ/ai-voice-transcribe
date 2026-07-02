import fs from "fs";
import { analyzeTranscript } from "../src/lib/analyzer";

const transcriptResult = {
  text: "n i n e e i g h t o n e s e v e n t w o",
  words: []
};

const result = analyzeTranscript(transcriptResult);
console.log(JSON.stringify(result, null, 2));
