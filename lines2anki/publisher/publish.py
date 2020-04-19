# -*- coding: utf-8 -*-
# Copyright: Kyle Hwang <feathered.hwang@hotmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# For release convenience
#


import os
import sys
import zipfile
from pathlib import Path

if __name__ == '__main__':
    dir_path = Path(sys.modules[__name__].__file__).parent.parent
    zf = zipfile.ZipFile(os.path.basename(dir_path) + '.ankiaddon', 'w', zipfile.ZIP_DEFLATED)
    files = os.listdir(dir_path)
    for filename in files:
        file_root, ext = os.path.splitext(filename)
        _ext = ext[1:].lower()
        if _ext == 'py':
            zf.write(os.path.join(dir_path, filename),
                     os.path.relpath(os.path.join(dir_path, filename), dir_path)
                     )
    zf.close()
