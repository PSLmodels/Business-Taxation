@echo off
:: USAGE: > cd conda.recipe
::        > remove_local_package
:: ACTION: (1) uninstall local biztax package (conda uninstall)
:: NOTE: for those with experience working with compiled languages,
::       removing a local conda package is analogous to a "make clean" operation
conda uninstall --yes -c local -n base biztax
exit 0
