import sys
import os
sys.path.append(os.getcwd())
if __name__=='__main__':
    mod = __import__('test_dyno', globals(), locals(), ['testing'], -1)
    f = getattr(mod, 'testing')
    f()
