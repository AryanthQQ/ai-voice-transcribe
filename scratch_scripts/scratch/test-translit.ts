const HINDI_TO_LATIN = {
  'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri',
  'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
  'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
  'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
  'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
  'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
  'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
  'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
  'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy',
  // Matras
  'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri',
  'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', 'ः': 'h', 'ँ': 'n',
  '्': '', // Halant (removes default 'a')
  '़': 'z', // Nuqta (approximate)
};

function transliterateHindiToHinglish(text: string): string {
  let result = '';
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (HINDI_TO_LATIN[char as keyof typeof HINDI_TO_LATIN]) {
      result += HINDI_TO_LATIN[char as keyof typeof HINDI_TO_LATIN];
      
      // If it's a consonant and no matra or halant follows, append 'a'
      const isConsonant = char >= 'क' && char <= 'ह';
      const hasMatraNext = nextChar && (
        (nextChar >= 'ा' && nextChar <= '्') || nextChar === '़'
      );
      
      // Basic heuristic: append 'a' unless it's the end of a word or followed by a matra
      if (isConsonant && !hasMatraNext && nextChar !== ' ' && nextChar !== undefined) {
        result += 'a';
      }
    } else {
      result += char;
    }
  }
  return result;
}

const testStrings = [
  "नमस्ते मेरा नाम एआई है",
  "आप कैसे हैं",
  "मादरचोद क्या कर रहा है"
];

for (const s of testStrings) {
  console.log(`${s} -> ${transliterateHindiToHinglish(s)}`);
}
