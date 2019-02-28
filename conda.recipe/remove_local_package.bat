@echo off
:: USAGE: ./remove_local_package.bat
:: ACTION: (1) uninstall installed biztax package (conda uninstall)
:: NOTE: for those with experience working with compiled languages,
::       removing a local conda package is analogous to a "make clean" operation
conda uninstall biztax --yes
exit 0
