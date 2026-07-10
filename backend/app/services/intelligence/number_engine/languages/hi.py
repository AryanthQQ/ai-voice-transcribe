from . import LanguageDefinition, register_language

hi = LanguageDefinition(code="hi", name="Hindi/Hinglish")

hi.add_digits({
    "shunya": "0", "zero": "0",
    "ek": "1",
    "do": "2",
    "teen": "3", "tin": "3",
    "chaar": "4", "char": "4",
    "paanch": "5", "panch": "5",
    "chhe": "6", "chhah": "6", "che": "6",
    "saat": "7", "sat": "7",
    "aath": "8", "ath": "8",
    "nau": "9", "no": "9",
})

# Hindi doesn't typically have a direct equivalent of "double" used before a number,
# but hinglish users often say "double" or "do baar"
hi.add_multipliers({
    "double": 2,
    "triple": 3,
    "do baar": 2,
    "teen baar": 3
})

register_language(hi)
