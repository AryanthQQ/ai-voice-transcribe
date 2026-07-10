from . import LanguageDefinition, register_language

en = LanguageDefinition(code="en", name="English")

en.add_digits({
    "zero": "0", "oh": "0", "o": "0",
    "one": "1", "won": "1",
    "two": "2", "to": "2", "too": "2",
    "three": "3", "tree": "3",
    "four": "4", "for": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8", "ate": "8",
    "nine": "9"
})

en.add_multipliers({
    "double": 2,
    "triple": 3,
    "two times": 2,
    "three times": 3
})

register_language(en)
