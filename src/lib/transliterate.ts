/**
 * Simple Devanagari to Latin (Hinglish) transliteration map
 */

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
  '्': '', // Halant
  '़': 'z', // Nuqta (approximate)
};

export function hindiToHinglish(text: string): string {
  if (!text) return "";
  
  let result = '';
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (HINDI_TO_LATIN[char as keyof typeof HINDI_TO_LATIN]) {
      result += HINDI_TO_LATIN[char as keyof typeof HINDI_TO_LATIN];
      
      const isConsonant = char >= 'क' && char <= 'ह';
      const hasMatraNext = nextChar && (
        (nextChar >= 'ा' && nextChar <= '्') || nextChar === '़'
      );
      
      if (isConsonant && !hasMatraNext && nextChar !== ' ' && nextChar !== undefined) {
        result += 'a';
      }
    } else {
      result += char;
    }
  }
  return result;
}
