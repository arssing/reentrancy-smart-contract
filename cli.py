import os
import re
import subprocess
import time

def get_bin_abi_by_code(path_to_sol):
    try:
        result = subprocess.Popen("solc --bin --abi "+ path_to_sol, shell=True, stdout=subprocess.PIPE)
    except Exception as e:
        raise e
    out = (result.stdout.read()).decode()
    sp = out.split('\n')
    return sp[3], sp[5]