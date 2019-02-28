@echo off
:: USAGE: ./install_local_package.bat
:: ACTION: (1) uninstall any installed package (remove_local_package.sh)
::         (2) executes "conda install conda-build" (if necessary)
::         (3) builds local biztax=0.0.0 package (conda build)
::         (4) installs local biztax=0.0.0 package (conda install)
:: NOTE: for those with experience working with compiled languages,
::       building a local conda package is analogous to compiling an executable
echo "STARTING ---"
echo "CLEANUP..."
:: uninstall any installed package
call remove_local_package.bat
echo "BUILD..."
:: build conda package for specified version of Python
conda build --old-build-string --python 3.6" .
echo "INSTALL..."
:: install conda package
conda install biztax=0.0.0 --use-local --yes
echo "CLEANUP..."
:: clean-up after package build
conda build purge
echo "FINISHED ---"
exit 0
