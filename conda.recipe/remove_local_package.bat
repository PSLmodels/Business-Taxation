@echo off
:: USAGE: > cd conda.recipe
::        > start "remove-local-package" remove_local_package.bat
:: ACTION: (1) uninstall _ANY_ installed biztax package (conda uninstall)
:: NOTE: for those with experience working with compiled languages,
::       removing a local conda package is analogous to a "make clean" operation
call conda uninstall --yes biztax
exit 0
