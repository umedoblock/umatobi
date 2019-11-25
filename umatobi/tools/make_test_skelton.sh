# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

#!/bin/bash

PYTHON_SCRIPT=${1}
# echo PYTHON_SCRIPT=${PYTHON_SCRIPT}

# HOW TO USE
# bash tools/make_test_skelton.sh simulator/node.py

egrep '^(class|    def) ' ${PYTHON_SCRIPT} \
  | sed -e 's:^    def ::' -e 's:(.*$::' \
  | awk '/^class/ {print $0"Tests(unittest.TestCase):\n"}
        !/^class/ {printf "    def test_"$0"(self):\n        pass\n\n"}' \
# :s:|:\r        |:g
