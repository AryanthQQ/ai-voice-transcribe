import re
import os
from transliterate import hindi_to_hinglish

# Word to Digit mapping for catching phone numbers spoken in words
NUMBER_WORDS_MAP = {
    "zero": "0", "shunya": "0", "sunya": "0",
    "one": "1", "ek": "1",
    "two": "2", "do": "2",
    "three": "3", "teen": "3", "tin": "3",
    "four": "4", "chaar": "4", "char": "4",
    "five": "5", "paanch": "5", "panch": "5",
    "six": "6", "chhe": "6", "che": "6", "chhah": "6",
    "seven": "7", "saat": "7",
    "eight": "8", "aath": "8", "ath": "8",
    "nine": "9", "nau": "9", "no": "9"
}

HINDI_DOUBLE_DIGITS = {
    "gyarah": "11", "barah": "12", "terah": "13", "chaudah": "14", "pandrah": "15",
    "solah": "16", "satrah": "17", "atharah": "18", "unnis": "19", "bees": "20",
    "ekkis": "21", "baais": "22", "teis": "23", "chaubis": "24", "pachis": "25",
    "chhabis": "26", "sattais": "27", "atthais": "28", "unatis": "29", "tees": "30",
    "iktis": "31", "battis": "32", "taitis": "33", "chautis": "34", "paintis": "35",
    "chhattis": "36", "saintis": "37", "adhtis": "38", "untalis": "39", "chalis": "40",
    "iktalis": "41", "bayalis": "42", "taitalis": "43", "chawalis": "44", "paitalis": "45",
    "chhiyalis": "46", "saintalis": "47", "adtalis": "48", "unchas": "49", "pachas": "50",
    "ikyawan": "51", "bawan": "52", "tirpan": "53", "chauwan": "54", "pachpan": "55",
    "chhappan": "56", "sattawan": "57", "atthawan": "58", "unsath": "59", "sath": "60",
    "iksath": "61", "basath": "62", "tirsath": "63", "chausath": "64", "painsath": "65",
    "chhiyasath": "66", "sarsath": "67", "adsath": "68", "unhattar": "69", "sattar": "70",
    "ikhattar": "71", "bahattar": "72", "tihattar": "73", "chauhattar": "74", "pachhattar": "75",
    "chhihattar": "76", "satahattar": "77", "athahattar": "78", "unasi": "79", "assi": "80",
    "ikyasi": "81", "bayasi": "82", "tirasi": "83", "chaurasi": "84", "pachasi": "85",
    "chhiyasi": "86", "satasi": "87", "atthasi": "88", "nawasi": "89", "nabbe": "90",
    "ikyanbe": "91", "banbe": "92", "tiranbe": "93", "chauranbe": "94", "pachanbe": "95",
    "chhiyanbe": "96", "satanbe": "97", "atthanbe": "98", "ninyanbe": "99",
    "sau": "00"
}

ENGLISH_DOUBLE_DIGITS = {
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
    "twenty": "20", "twenty one": "21", "twenty two": "22", "twenty three": "23", "twenty four": "24",
    "twenty five": "25", "twenty six": "26", "twenty seven": "27", "twenty eight": "28", "twenty nine": "29",
    "thirty": "30", "thirty one": "31", "thirty two": "32", "thirty three": "33", "thirty four": "34",
    "thirty five": "35", "thirty six": "36", "thirty seven": "37", "thirty eight": "38", "thirty nine": "39",
    "forty": "40", "forty one": "41", "forty two": "42", "forty three": "43", "forty four": "44",
    "forty five": "45", "forty six": "46", "forty seven": "47", "forty eight": "48", "forty nine": "49",
    "fifty": "50", "fifty one": "51", "fifty two": "52", "fifty three": "53", "fifty four": "54",
    "fifty five": "55", "fifty six": "56", "fifty seven": "57", "fifty eight": "58", "fifty nine": "59",
    "sixty": "60", "sixty one": "61", "sixty two": "62", "sixty three": "63", "sixty four": "64",
    "sixty five": "65", "sixty six": "66", "sixty seven": "67", "sixty eight": "68", "sixty nine": "69",
    "seventy": "70", "seventy one": "71", "seventy two": "72", "seventy three": "73", "seventy four": "74",
    "seventy five": "75", "seventy six": "76", "seventy seven": "77", "seventy eight": "78", "seventy nine": "79",
    "eighty": "80", "eighty one": "81", "eighty two": "82", "eighty three": "83", "eighty four": "84",
    "eighty five": "85", "eighty six": "86", "eighty seven": "87", "eighty eight": "88", "eighty nine": "89",
    "ninety": "90", "ninety one": "91", "ninety two": "92", "ninety three": "93", "ninety four": "94",
    "ninety five": "95", "ninety six": "96", "ninety seven": "97", "ninety eight": "98", "ninety nine": "99"
}

# Merge both maps
NUMBER_WORDS_MAP.update(HINDI_DOUBLE_DIGITS)
NUMBER_WORDS_MAP.update(ENGLISH_DOUBLE_DIGITS)

# Load bad words from txt
bad_words_path = os.path.join(os.path.dirname(__file__), "bad_words.txt")
try:
    with open(bad_words_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\\n", "\n")
        PROFANITY_WORDS = [w.strip().lower() for w in content.split("\n") if w.strip()]
except:
    PROFANITY_WORDS = ["fuck", "shit", "bitch", "bastard"]

THREATS = [
    # English
    r"i'?ll kill you", r"i will kill you", r"kill yourself", r"i'?m going to hurt you",
    r"going to beat you", r"i'?ll beat you", r"i will destroy you", r"i'?ll destroy you",
    r"i will end you", r"watch your back", r"you'?re dead", r"i'?ll find you",
    r"break your leg", r"smash your face", r"ruin your life", r"teach you a lesson", 
    r"cut you", r"make you pay", r"shoot you", r"stab you", r"slap you", r"punch you",
    # Hindi/Hinglish
    r"maar dunga", r"jaan se maar", r"jan se maar", r"thok dunga", r"tod dunga",
    r"maar d?al?unga", r"khatam kar d?ung[ae]", r"zinda gaad d?unga",
    r"chhodunga nahi", r"tange tod dunga", r"teri aisi ki taisi",
    # Tamil
    r"konnu poduven", r"kollamal vida", r"adimai aakiruven",
    # Telugu
    r"sampestha", r"ninnu vadalanu", r"champestha",
    # Bengali
    r"mere felbo", r"khun kore", r"sesh kore", r"bhenge debo",
    # Marathi
    r"marun taken", r"tangle moden",
    # Punjabi
    r"goli maar", r"latt tor", r"jaan toh maar"
]

SCAMS = [
    r"\botp\b", r"one time password", r"cvv", r"share your pin", r"upi pin",
    r"atm pin", r"credit card number", r"card number", r"bank details", r"account number",
    r"you (have )?won", r"lucky (winner|draw)", r"lottery", r"prize money",
    r"transfer (the )?money", r"wire transfer", r"gift card", r"bitcoin",
    r"investment (opportunity|plan|scheme)", r"double your money", r"guaranteed returns",
    r"kyc (expire|update|verif)", r"tax refund", r"verify your account", r"suspended",
    r"otp batao", r"cvv batao"
]

def analyze_text(text: str):
    # 1. Transliterate Devanagari to Hinglish so Latin bad words list works
    transliterated = hindi_to_hinglish(text)
    
    # 2. Lowercase and pad
    lower_text = " " + transliterated.lower() + " "
    
    # 2.5 Convert number words to digits for PII catching
    # e.g., "nau aath saat" -> "9 8 7"
    digitized_text = lower_text
    # We sort keys by length descending to replace longer words first (e.g., "twenty one" before "twenty")
    sorted_number_words = sorted(NUMBER_WORDS_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for word, digit in sorted_number_words:
        # Replace whole words only
        digitized_text = re.sub(rf"\b{word}\b", digit, digitized_text)
    stats = {
        "profanity": 0,
        "threat": 0,
        "scam": 0,
        "pii": 0
    }
    flags = {
        "abuse_detected": False,
        "threat_detected": False,
        "phone_shared": False
    }
    
    # 1. Profanity
    for word in PROFANITY_WORDS:
        # Avoid partial word matches like 'hello' matching 'hell' by checking boundaries
        # Since some words have asterisks or chars, just use basic word boundaries
        escaped = re.escape(word).replace(r"\*", r"[a-z]?")
        pattern = r"(^|[^a-z])(" + escaped + r")([^a-z]|$)"
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            stats["profanity"] += matches
            flags["abuse_detected"] = True

    # 2. Threats
    for pattern in THREATS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            stats["threat"] += matches
            flags["threat_detected"] = True

    # 3. Scams
    for pattern in SCAMS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            stats["scam"] += matches

    # 4. PII - phone numbers (extremely aggressive detection)
    # Catches 10-14 digits, with or without +91, with spaces between digits (e.g., 9 8 7 6...)
    phone_pattern = r"(?:(?:\+91|91)?[ -]?)?\b\d[ \-\d]{8,13}\d\b"
    sensitive_num = r"\b\d(?:[\s-]?\d){3,}\b"
    
    pii_matches = re.findall(phone_pattern, digitized_text) + re.findall(sensitive_num, digitized_text)
    if len(pii_matches) > 0:
        stats["pii"] = len(pii_matches)
        flags["phone_shared"] = True

    # Risk Score calculation
    risk_score = (stats["threat"] * 22) + (stats["scam"] * 12) + (stats["profanity"] * 6) + (stats["pii"] * 60)
    risk_score = min(100, risk_score)
    
    risk_level = "Safe"
    if risk_score >= 60: risk_level = "Critical"
    elif risk_score >= 35: risk_level = "High"
    elif risk_score >= 12: risk_level = "Moderate"

    return {
        "stats": stats,
        "flags": flags,
        "risk_score": risk_score,
        "risk_level": risk_level
    }
