from __future__ import print_function,division,unicode_literals

import sys,os
import pickle
import subprocess

if __name__ == '__main__':
    assert len(sys.argv) == 1
    if sys.version_info.major >= 3:
        cmd = '/usr/bin/python3'
    else:
        cmd = '/usr/bin/python'
    dbfile = '__pycache__/all_examples_stdout.pyd'
    dir = os.path.abspath(os.path.dirname(__file__))
    files = os.listdir(dir)
    ret = dict()
    fn = os.path.join(dir,dbfile)
    if os.path.exists(fn):
        with open(fn,'rb') as fh:
            refout = pickle.load(fh)
    else:
        refout = dict()
    failed = []
    mismatch = []
    match = []
    for fn in sorted(files):
        if fn == os.path.split(__file__)[-1] or os.path.splitext(fn)[-1] != '.py':
            continue
        print('*'*35 + ' %s '%fn.center(10) + '*'*35)
        ffn = os.path.join(dir,fn)
        try:
            outp = subprocess.check_output([cmd,ffn], close_fds=True)
            if sys.version_info.major >= 3:
                outp = str(outp,'utf-8')
        except subprocess.CalledProcessError as ex:
            if sys.version_info.major >= 3:
                outp = str(ex.output,'utf-8') + '\n*** returncode: %d'%ex.returncode
            else:
                outp = ex.output + '\n*** returncode: %d'%ex.returncode
            print(outp)
            print('!'*35 + ' %s failed '%fn.center(10) + '!'*35)
            failed.append(fn)
        else:
            print(outp)
        if fn in refout:
            if refout[fn].strip()!=outp.strip():
                print('-'*35 + ' %s mismatch '%fn.center(10) + '-'*35)
                mismatch.append(fn)
            else:
                print('+'*35 + ' %s match '%fn.center(10) + '+'*35)
                match.append(fn)
        ret[fn] = outp
    
    print('*'*35 + ' These demos matched: ' + '*'*35)
    print('\n'.join(match))
    print('*'*35 + ' These demos did not match but did not fail either: ' + '*'*35)
    print('\n'.join([fn for fn in mismatch if fn not in failed]))
    print('*'*35 + ' These demos failed: ' + '*'*35)
    print('\n'.join(failed))

    fn = os.path.join(dir,dbfile)
    if not os.path.exists(fn):
        with open(fn,'wb') as fh:
            pickle.dump(ret,fh,-1)



