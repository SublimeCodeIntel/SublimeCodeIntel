#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006 Bermi Ferrer Martinez
# info at bermi dot org
# See the end of this file for the free software, open source license
# (BSD-style).

import re
from Base import Base


class Spanish (Base):
    """
    Inflector for pluralize and singularize Spanish nouns.
    """

    def pluralize(self, word):
        """Pluralizes Spanish nouns."""
        rules = [
            [u"(?i)([aeiou])x$", u"\\1x"],
            # This could fail if the word is oxytone.
            [u"(?i)([áéíóú])([ns])$", u"|1\\2es"],
            [u"(?i)(^[bcdfghjklmnñpqrstvwxyz]*)an$",
                u"\\1anes"],  # clan->clanes
            [u"(?i)([áéíóú])s$", u"|1ses"],
            [u"(?i)(^[bcdfghjklmnñpqrstvwxyz]*)([aeiou])([ns])$",
                u"\\1\\2\\3es"],  # tren->trenes
            [u"(?i)([aeiouáéó])$", u"\\1s"],
            # casa->casas, padre->padres, papá->papás
            [u"(?i)([aeiou])s$", u"\\1s"],  # atlas->atlas, virus->virus, etc.
            [u"(?i)([éí])(s)$", u"|1\\2es"],  # inglés->ingleses
            [u"(?i)z$", u"ces"],  # luz->luces
            [u"(?i)([íú])$", u"\\1es"],  # ceutí->ceutíes, tabú->tabúes
            [u"(?i)(ng|[wckgtp])$", u"\\1s"],
            # Anglicismos como puenting, frac, crack, show (En que casos
            # podría fallar esto?)
            [u"(?i)$", u"es"]   # ELSE +es (v.g. árbol->árboles)
        ]

        uncountable_words = [
            u"tijeras", u"gafas", u"vacaciones", u"víveres", u"déficit"]
        """ In fact these words have no singular form: you cannot say neither
        "una gafa" nor "un vívere". So we should change the variable name to
        onlyplural or something alike."""

        irregular_words = {
            u"país": u"países",
            u"champú": u"champús",
            u"jersey": u"jerséis",
            u"carácter": u"caracteres",
            u"espécimen": u"especímenes",
            u"menú": u"menús",
            u"régimen": u"regímenes",
            u"curriculum": u"currículos",
            u"ultimátum": u"ultimatos",
            u"memorándum": u"memorandos",
            u"referéndum": u"referendos"
        }

        lower_cased_word = word.lower()

        for uncountable_word in uncountable_words:
            if lower_cased_word[-1 * len(uncountable_word):] == uncountable_word:
                return word

        for irregular in irregular_words.keys():
            match = re.search(
                u"(?i)(u" + irregular + u")$", word, re.IGNORECASE)
            if match:
                return re.sub(u"(?i)" + irregular + u"$", match.expand(u"\\1")[0] + irregular_words[irregular][1:], word)

        for rule in range(len(rules)):
            match = re.search(rules[rule][0], word, re.IGNORECASE)

            if match:
                groups = match.groups()
                replacement = rules[rule][1]
                if re.match(u"\|", replacement):
                    for k in range(1, len(groups)):
                        replacement = replacement.replace(u"|" + str(k), self.string_replace(
                            groups[k - 1], u"ÁÉÍÓÚáéíóú", u"AEIOUaeiou"))

                result = re.sub(rules[rule][0], replacement, word)
                # Esto acentua los sustantivos que al pluralizarse se
                # convierten en esdrújulos como esmóquines, jóvenes...
                match = re.search(u"(?i)([aeiou]).{1,3}([aeiou])nes$", result)

                if match and len(match.groups()) > 1 and not re.search(u"(?i)[áéíóú]", word):
                    result = result.replace(match.group(0), self.string_replace(
                        match.group(1), u"AEIOUaeiou", u"ÁÉÍÓÚáéíóú") + match.group(0)[1:])

                return result

        return word

    def singularize(self, word):
        """Singularizes Spanish nouns."""

        rules = [
            [u"(?i)^([bcdfghjklmnñpqrstvwxyz]*)([aeiou])([ns])es$",
                u"\\1\\2\\3"],
            [u"(?i)([aeiou])([ns])es$",  u"~1\\2"],
            [u"(?i)oides$",  u"oide"],  # androides->androide
            [u"(?i)(ces)$/i", u"z"],
            [u"(?i)(sis|tis|xis)+$",  u"\\1"],  # crisis, apendicitis, praxis
            [u"(?i)(é)s$",  u"\\1"],  # bebés->bebé
            [u"(?i)([^e])s$",  u"\\1"],  # casas->casa
            [u"(?i)([bcdfghjklmnñprstvwxyz]{2,}e)s$", u"\\1"],  # cofres->cofre
            [u"(?i)([ghñpv]e)s$", u"\\1"],  # 24-01 llaves->llave
            [u"(?i)es$", u""]  # ELSE remove _es_  monitores->monitor
        ]

        uncountable_words = [
            u"paraguas", u"tijeras", u"gafas", u"vacaciones", u"víveres", u"lunes",
            u"martes", u"miércoles", u"jueves", u"viernes", u"cumpleaños", u"virus", u"atlas", u"sms"]

        irregular_words = {
            u"jersey": u"jerséis",
            u"espécimen": u"especímenes",
            u"carácter": u"caracteres",
            u"régimen": u"regímenes",
            u"menú": u"menús",
            u"régimen": u"regímenes",
            u"curriculum": u"currículos",
            u"ultimátum": u"ultimatos",
            u"memorándum": u"memorandos",
            u"referéndum": u"referendos",
            u"sándwich": u"sándwiches"
        }

        lower_cased_word = word.lower()

        for uncountable_word in uncountable_words:
            if lower_cased_word[-1 * len(uncountable_word):] == uncountable_word:
                return word

        for irregular in irregular_words.keys():
            match = re.search(u"(u" + irregular + u")$", word, re.IGNORECASE)
            if match:
                return re.sub(u"(?i)" + irregular + u"$", match.expand(u"\\1")[0] + irregular_words[irregular][1:], word)

        for rule in range(len(rules)):
            match = re.search(rules[rule][0], word, re.IGNORECASE)
            if match:
                groups = match.groups()
                replacement = rules[rule][1]
                if re.match(u"~", replacement):
                    for k in range(1, len(groups)):
                        replacement = replacement.replace(u"~" + str(
                            k), self.string_replace(groups[k - 1], u"AEIOUaeiou", u"ÁÉÍÓÚáéíóú"))

                result = re.sub(rules[rule][0], replacement, word)
                # Esta es una posible solución para el problema de dobles
                # acentos. Un poco guarrillo pero funciona
                match = re.search(u"(?i)([áéíóú]).*([áéíóú])", result)

                if match and len(match.groups()) > 1 and not re.search(u"(?i)[áéíóú]", word):
                    result = self.string_replace(
                        result, u"ÁÉÍÓÚáéíóú", u"AEIOUaeiou")

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
