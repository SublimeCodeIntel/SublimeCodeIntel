"""Add these files to the lexers/scintilla tree."""

def remove(config):
    return [
        "lexers/LexTCL.cxx",
    ]

def add(config):
    return [
        ("cons", "."),
        ("lexers", "lexers", "force"),
    ]

