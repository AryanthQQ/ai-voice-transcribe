from . import LanguageDefinition, register_language

gu = LanguageDefinition(code="gu", name="Gujarati")

gu.add_digits({
    "shunya": "0",
    "ek": "1",
    "be": "2",
    "tran": "3",
    "chaar": "4", "char": "4",
    "paanch": "5", "panch": "5",
    "chha": "6",
    "saat": "7", "sat": "7",
    "aath": "8", "ath": "8",
    "nav": "9",
})

gu.add_multipliers({
    "be vakhat": 2,
    "tran vakhat": 3
})

register_language(gu)
