#!/bin/bash
# USAGE: ./remove_local_package.sh
# ACTION: (1) uninstalls any installed biztax package (conda uninstall)
# NOTE: for those with experience working with compiled languages,
#       removing a local conda package is analogous to a "make clean" operation

# uninstall any existing biztax conda package
conda list biztax | awk '$1=="biztax"{rc=1}END{exit(rc)}'
if [[ $? -eq 1 ]]; then
    conda uninstall biztax --yes 2>&1 > /dev/null
fi

exit 0
