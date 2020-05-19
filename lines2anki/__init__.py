# -*- coding: utf-8 -*-
# Copyright: Kyle Hwang <feathered.hwang@hotmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Anki add-on for importing lines of movie and TV series as new notes, composed by
 audio media and subtitle. User is able to map properties of the imported file
 to fields in a note type.

Much thanks to https://github.com/hssm/media-import, from whom I mocked the
 structure of programme.

See github page to report issues or to contribute:
https://github.com/feathered-hwang/lines2anki
"""


# set up logging to file - see previous section for more details
import logging
import os
import sys


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=os.path.dirname(sys.modules[__name__].__file__) + '/logger.log',
                    filemode='w')
# print the module's directory
logging.info(os.path.dirname(sys.modules[__name__].__file__))


# import Lines Import... main module
from . import importation

# TODO: import a detailed beautified model
# from . import builtinModel

# import test module if exist
try:
    from .testing import test
except ImportError:
    logging.info("test module doesn't exist.")
