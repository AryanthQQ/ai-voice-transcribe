import unicodedata

HINDI_TO_LATIN = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy',
    'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'ड़': 'd', 'ढ़': 'dh', 'फ़': 'f', 'य़': 'y',
    # Matras
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', 'ः': 'h', 'ँ': 'n',
    '्': '', # Halant
    '़': '', # Nuqta (if uncombined, ignore or approximate)
}

def hindi_to_hinglish(text: str) -> str:
    if not text:
        return ""
    
    # Pre-compose characters so Nuqta combined with consonant becomes a single char
    text = unicodedata.normalize('NFC', text)
    
    result = ""
    for i, char in enumerate(text):
        next_char = text[i + 1] if i + 1 < len(text) else None
        
        if char in HINDI_TO_LATIN:
            # For w/v sounds
            if char == 'व' or char == 'ब':
                if i == 0 or (text[i-1] == ' '):
                    # Usually wafayein not bafaye
                    pass
            
            result += HINDI_TO_LATIN[char]
            
            is_consonant = ('क' <= char <= 'ह') or ('क़' <= char <= 'य़')
            has_matra_next = next_char and (
                next_char in ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'े', 'ै', 'ो', 'ौ', '्', '़']
            )
            
            # Schwa deletion: do NOT add 'a' if it's the end of a word (next_char is None or non-word)
            # or if it's a specific ending cluster
            is_end_of_word = next_char is None or (not next_char.isalnum() and next_char not in HINDI_TO_LATIN)
            
            if is_consonant and not has_matra_next and not is_end_of_word:
                result += 'a'
        else:
            result += char
            
    return result

print(hindi_to_hinglish("दिल तोड़कर हसती है मेरा वफ़ाए तुम्हें याद आएगी"))
print(hindi_to_hinglish("क्या कह रहे हैं टूट गा भी किसका जिसने आपसे दिल लगाया उसी का दिल टूट गया है"))
print(hindi_to_hinglish("मैं हूँ इस समय इंडिया गेट के पास समान लेने के लिए यही क्रोकरी वगेरह"))
print(hindi_to_hinglish("कोल कट कट के मेरे मा ही चोद दी कल रात में"))
print(hindi_to_hinglish("खड़े लंड पर धोखा दे दिया"))
