# -*- coding: utf-8 -*-
# Copyright: Kyle Hwang <feathered.hwang@hotmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Standard Lines model.
#

import anki.stdmodels
from anki.collection import _Collection


def add_lines_model(col: _Collection):
    mm = col.models
    m = mm.new(_('Lines'))
    field_names = (
        'Audio',
        'Line',
        'Background',
        'Provenance'
    )
    for n in field_names:
        mm.addField(m, mm.newField(_(n)))

    t = mm.newTemplate(_("Test"))
    # css
    # TODO Add CSS

    # recognition card
    t['qfmt'] = "<div class=audio> {{Audio}} </div>"
    t['afmt'] = """
{{Front}}\n\n
<he id=answer>\n\n
<div class=line> {{Line}} </div><br>\n
"""
    mm.addTemplate(m, t)
    mm.add(m)
    return m


anki.stdmodels.models.append((_("Lines"), add_lines_model))
