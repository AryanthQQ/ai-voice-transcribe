import fs from "fs";

const NUMBER_MAP: Record<string, string> = {
  "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
  "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
  "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90",
  "hundred": "00", "thousand": "000"
};

const keys = Object.keys(NUMBER_MAP);

function parseRunOnNumbers(s: string): string | null {
  // We want to see if the entire string `s` can be formed by a sequence of `keys`,
  // allowing up to 1 character of overlap between consecutive words.
  // dp[i] will store the sequence of mapped digits up to index i, or null if impossible.
  const dp: (string | null)[] = new Array(s.length + 1).fill(null);
  dp[0] = "";

  for (let i = 0; i <= s.length; i++) {
    if (dp[i] !== null) {
      for (const key of keys) {
        // Try without overlap
        if (s.startsWith(key, i)) {
          const nextIdx = i + key.length;
          dp[nextIdx] = dp[i] + NUMBER_MAP[key];
        }
        // Try with 1 character overlap (the first character of key overlaps with the last character before i)
        if (i > 0 && s[i - 1] === key[0] && s.startsWith(key.substring(1), i)) {
          const nextIdx = i + key.length - 1;
          dp[nextIdx] = dp[i] + NUMBER_MAP[key];
        }
      }
    }
  }

  return dp[s.length];
}

console.log(parseRunOnNumbers("nineighttwentyeighttwofour"));
console.log(parseRunOnNumbers("nineightoneseventwo"));
console.log(parseRunOnNumbers("nineeightoneseventwo"));
