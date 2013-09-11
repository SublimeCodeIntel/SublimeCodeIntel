#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006 Bermi Ferrer Martinez
# info at bermi dot org
# See the end of this file for the free software, open source license
# (BSD-style).

import re
from .Base import Base


class Spanish (Base):
    """
    Inflector for pluralize and singularize Spanish nouns.
    """

    def pluralize(self, word):
        """Pluralizes Spanish nouns."""
        rules = [
            ["(?i)([aeiou])x$", "\\1x"],
            # This could fail if the word is oxytone.
            ["(?i)([áéíóú])([ns])$", "|1\\2es"],
            ["(?i)(^[bcdfghjklmnñpqrstvwxyz]*)an$",
                "\\1anes"],  # clan->clanes
            ["(?i)([áéíóú])s$", "|1ses"],
            ["(?i)(^[bcdfghjklmnñpqrstvwxyz]*)([aeiou])([ns])$",
                "\\1\\2\\3es"],  # tren->trenes
            ["(?i)([aeiouáéó])$", "\\1s"],
            # casa->casas, padre->padres, papá->papás
            ["(?i)([aeiou])s$", "\\1s"],  # atlas->atlas, virus->virus, etc.
            ["(?i)([éí])(s)$", "|1\\2es"],  # inglés->ingleses
            ["(?i)z$", "ces"],  # luz->luces
            ["(?i)([íú])$", "\\1es"],  # ceutí->ceutíes, tabú->tabúes
            ["(?i)(ng|[wckgtp])$", "\\1s"],
            # Anglicismos como puenting, frac, crack, show (En que casos
            # podría fallar esto?)
            ["(?i)$", "es"]   # ELSE +es (v.g. árbol->árboles)
        ]

        uncountable_words = [
            "tijeras", "gafas", "vacaciones", "víveres", "déficit"]
        """ In fact these words have no singular form: you cannot say neither
        "una gafa" nor "un vívere". So we should change the variable name to
        onlyplural or something alike."""

        irregular_words = {
            "país": "países",
            "champú": "champús",
            "jersey": "jerséis",
            "carácter": "caracteres",
            "espécimen": "especímenes",
            "menú": "menús",
            "régimen": "regímenes",
            "curriculum": "currículos",
            "ultimátum": "ultimatos",
            "memorándum": "memorandos",
            "referéndum": "referendos"
        }

        lower_cased_word = word.lower()

        for uncountable_word in uncountable_words:
            if lower_cased_word[-1 * len(uncountable_word):] == uncountable_word:
                return word

        for irregular in list(irregular_words.keys()):
            match = re.search(
                "(?i)(u" + irregular + ")$", word, re.IGNORECASE)
            if match:
                return re.sub("(?i)" + irregular + "$", match.expand("\\1")[0] + irregular_words[irregular][1:], word)

        for rule in range(len(rules)):
            match = re.search(rules[rule][0], word, re.IGNORECASE)

            if match:
                groups = match.groups()
                replacement = rules[rule][1]
                if re.match("\|", replacement):
                    for k in range(1, len(groups)):
                        replacement = replacement.replace("|" + str(k), self.string_replace(
                            groups[k - 1], "ÁÉÍÓÚáéíóú", "AEIOUaeiou"))

                result = re.sub(rules[rule][0], replacement, word)
                # Esto acentua los sustantivos que al pluralizarse se
                # convierten en esdrújulos como esmóquines, jóvenes...
                match = re.search("(?i)([aeiou]).{1,3}([aeiou])nes$", result)

                if match and len(match.groups()) > 1 and not re.search("(?i)[áéíóú]", word):
                    result = result.replace(match.group(0), self.string_replace(
                        match.group(1), "AEIOUaeiou", "ÁÉÍÓÚáéíóú") + match.group(0)[1:])

                return result

        return word

    def singularize(self, word):
        """Singularizes Spanish nouns."""

        rules = [
            ["(?i)^([bcdfghjklmnñpqrstvwxyz]*)([aeiou])([ns])es$",
                "\\1\\2\\3"],
            ["(?i)([aeiou])([ns])es$",  "~1\\2"],
            ["(?i)oides$",  "oide"],  # androides->androide
            ["(?i)(ces)$/i", "z"],
            ["(?i)(sis|tis|xis)+$",  "\\1"],  # crisis, apendicitis, praxis
            ["(?i)(é)s$",  "\\1"],  # bebés->bebé
            ["(?i)([^e])s$",  "\\1"],  # casas->casa
            ["(?i)([bcdfghjklmnñprstvwxyz]{2,}e)s$", "\\1"],  # cofres->cofre
            ["(?i)([ghñpv]e)s$", "\\1"],  # 24-01 llaves->llave
            ["(?i)es$", ""]  # ELSE remove _es_  monitores->monitor
        ]

        uncountable_words = [
            "paraguas", "tijeras", "gafas", "vacaciones", "víveres", "lunes",
            "martes", "miércoles", "jueves", "viernes", "cumpleaños", "virus", "atlas", "sms"]

        irregular_words = {
            "jersey": "jerséis",
            "espécimen": "especímenes",
            "carácter": "caracteres",
            "régimen": "regímenes",
            "menú": "menús",
            "régimen": "regímenes",
            "curriculum": "currículos",
            "ultimátum": "ultimatos",
            "memorándum": "memorandos",
            "referéndum": "referendos",
            "sándwich": "sándwiches"
        }

        lower_cased_word = word.lower()

        for uncountable_word in uncountable_words:
            if lower_cased_word[-1 * len(uncountable_word):] == uncountable_word:
                return word

        for irregular in list(irregular_words.keys()):
            match = re.search("(u" + irregular + ")$", word, re.IGNORECASE)
            if match:
                return re.sub("(?i)" + irregular + "$", match.expand("\\1")[0] + irregular_words[irregular][1:], word)

        for rule in range(len(rules)):
            match = re.search(rules[rule][0], word, re.IGNORECASE)
            if match:
                groups = match.groups()
                replacement = rules[rule][1]
                if re.match("~", replacement):
                    for k in range(1, len(groups)):
                        replacement = replacement.replace("~" + str(
                            k), self.string_replace(groups[k - 1], "AEIOUaeiou", "ÁÉÍÓÚáéíóú"))

                result = re.sub(rules[rule][0], replacement, word)
                # Esta es una posible solución para el problema de dobles
                # acentos. Un poco guarrillo pero funciona
                match = re.search("(?i)([áéíóú]).*([áéíóú])", result)

                if match and len(match.groups()) > 1 and not re.search("(?i)[áéíóú]", word):
                    result = self.string_replace(
                        result, "ÁÉÍÓÚáéíóú", "AEIOUaeiou")

                return result

        return word


# Copyright (c) 2006 Bermi Ferrer Martinez
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software to deal in this software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of this software, and to permit
# persons to whom this software is furnished to do so, subject to the following
# condition:
#
# THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THIS SOFTWARE.
