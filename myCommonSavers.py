# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

import pickle
import os


def saver(sth, fileName: str):
    """Save *sth* to *fileName* with pickle.

    You'd better give a file name ending with ``.data``.
    """
    with open(fileName, 'wb') as f:
        pickle.dump(sth, f)


def reader(fileName: str):
    """Load and return the object pickled in *fileName*."""
    with open(fileName, 'rb') as f:
        return pickle.load(f)


def checkPath(path: str):
    """Create the folder *path* if it does not exist yet."""
    if path != '':
        if not os.path.exists(path):
            os.makedirs(path)
