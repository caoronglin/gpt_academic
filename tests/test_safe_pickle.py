def validate_path():
    import os
    import sys

    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # validate path so you can run from base directory

from crazy_functions.latex_fns.latex_actions import (LatexPaperFileGroup,
                                                     LatexPaperSplit)
from crazy_functions.latex_fns.latex_pickle_io import objdump, objload

pfg = LatexPaperFileGroup()
pfg.get_token_num = None
pfg.target = "target_elem"
x = objdump(pfg)
t = objload()

print(t.target)
