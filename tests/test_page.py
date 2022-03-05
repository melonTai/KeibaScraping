import unittest
import doctest
import sys
sys.path.append('../scrapenetkeiba')
from scrapenetkeiba.page import *

if __name__ == '__main__':
    import doctest
    import sys
    import inspect
    flags = doctest.FAIL_FAST|doctest.REPORT_NDIFF
    __test__ = {}
    pre_globals = globals().copy()
    for key, obj in pre_globals.items():
        for m in inspect.getmembers(obj):
            __test__[f"{key}.{m[0]}"] = m[1]
    if len(sys.argv) > 1:
        name = sys.argv[1]
        verbose = len(sys.argv) > 2 and sys.argv[2] == "-v"
        if name in globals():
            obj = globals()[name]
        else:
            obj = __test__[name]
        doctest.run_docstring_examples(obj, globals(), name=name,
                                       optionflags=flags, verbose=verbose)
    else:
        verbose = len(sys.argv) > 1 and sys.argv[1] == "-v"
        fail, total = doctest.testmod(optionflags=flags, verbose=verbose)
        print("{} failures out of {} tests".format(fail, total))