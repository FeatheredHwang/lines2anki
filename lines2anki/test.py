# -*- coding: utf-8 -*-
# Copyright: Kyle Hwang <feathered.hwang@hotmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# for testing convenience
#
import logging

from PyQt5.QtWidgets import QAction
from aqt import mw


def do_test():
    """
    For testing convenience
    """
    logging.info('Hello World!')


test_action = QAction("TEST", mw)
test_action.triggered.connect(do_test)
mw.form.menuTools.addAction(test_action)