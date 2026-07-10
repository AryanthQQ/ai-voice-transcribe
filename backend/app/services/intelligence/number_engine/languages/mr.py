from . import LanguageDefinition, register_language

mr = LanguageDefinition(code="mr", name="Marathi")

mr.add_digits({
    "shunya": "0",
    "ek": "1",
    "don": "2",
    "teen": "3", "tin": "3",
    "chaar": "4", "char": "4",
    "paach": "5", "pach": "5",
    "saha": "6",
    "saat": "7", "sat": "7",
    "aath": "8", "ath": "8",
    "nau": "9",
})

mr.add_multipliers({
    "don vela": 2,
    "teen vela": 3
})

register_language(mr)
