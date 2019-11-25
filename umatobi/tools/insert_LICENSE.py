# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, re

from umatobi.constants import *

LICENSE_c = """
/* umatobi simulator
 *
 * Copyright (c) 2012-2019 梅濁酒(=umedoblock)
 *
 * This software is released under the MIT License.
 * https://github.com/umedoblock/umatobi
 */
"""

LICENSE_py = """# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

"""

# 2012-201. => 2012-2019

if __name__ == "__main__":
    # python3 tools/insert_LICENSE.py > skipped.log
    import glob
    candidate_files = []
    skipped_files = []
   #print(os.path.join(UMATOBI_ROOT_PATH, '..'))
    for file_name in glob.glob(os.path.join(UMATOBI_ROOT_PATH, '../**'), recursive=True):
        if re.search(r'(tests/umatobi-simulation|__pycache__|mock_studying|umatobi\.egg-info)', file_name):
            continue
        if re.search(r'(LICENSE)', file_name):
            continue
        DOCUMENTS = 'LICENSE|NOTE|HOW_TO_DEVELOP|INSTALL|README|release\.txt|umatobiAlgo\.txt'
        # awk -F. '{print $NF}' skipped.log | egrep -v '(=|/)' | sort | uniq
        exts = 'c|h|py|sh'
        if re.search(fr'({DOCUMENTS}|Makefile|(\.({exts}))$)', file_name):
            candidate_files.append(file_name)
        else:
            skipped_files.append(file_name)
       #print("file_name =", file_name)
   #print('candidate_files =')
   #print('\n'.join(candidate_files))
   #print()
   #print('skipped_files =')
   #print('\n'.join(skipped_files))

    for candidate_file in candidate_files:
        exts = 'c|h'
        if re.search(fr'(\.({exts})$)', candidate_file):
            LICENSE = LICENSE_c
        else:
            LICENSE = LICENSE_py
        with open(candidate_file, "r") as f:
            codes = f.read()
        with open(candidate_file, "w") as f:
            print(LICENSE + codes, file=f, end="")
