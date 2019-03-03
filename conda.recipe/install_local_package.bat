@echo off
:: USAGE: ./install_local_package.bat
:: ACTION: (1) build local biztax=0.0.0 package (conda build)
::         (2) install local biztax=0.0.0 package (conda install)
::         (3) clean-up build intermediates (conda build purge)
:: NOTE: for those with experience working with compiled languages,
::       building a local conda package is analogous to compiling an executable
echo "STARTING ---"
echo "BUILD..."
:: build conda package for specified version of Python
conda build --old-build-string --no-anaconda-upload -c PSLmodels --python 3.6 .
::     If want to use local (instead of PSLmodels) package(s),
::     replace "-c PSLmodels" with "-c local" in above conda build command.
echo "INSTALL..."
:: install local conda package
conda install --yes -c local -n base biztax=0.0.0
::     If above command does not work, try variants of this command:
::     conda install -n base C:\Users\cody_\Anaconda3\conda-bld\win-64\biztax-0.0.0-py37_0.tar.bz2
echo "CLEANUP..."
:: clean-up intermediate build files after package build
:: TEMP conda build purge
echo "FINISHED ---"
exit 0
