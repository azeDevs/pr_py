from core.az_terminal import PR_LN
from utils.util_print import PR_FUNC, PRINT_DEPS, PRINT_RUN


PRINT_RUN('PR_FUNC')
PRINT_DEPS('PR_FUNC')
PR_LN("", pre=False, suf=False)

def testfunc():
    PR_FUNC('single_proc', 'file', ic="A", ln=True)
    PR_FUNC('multi_proc', 'file', ic="B", ln=True)


testfunc()
print('\n'*4)