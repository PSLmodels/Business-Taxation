@echo off
:: USAGE: > cd conda.recipe
::        > install_local_package
:: ACTION: (1) build local biztax=0.0.0 package (conda build)
::         (2) install local biztax=0.0.0 package (conda install)
::         (3) clean-up build intermediates (conda build purge)
:: NOTE: for those with experience working with compiled languages,
::       building a local conda package is analogous to compiling an executable
echo "STARTING ---"
echo "BUILD..."
:: build conda package
set OPTIONS="--old-build-string --no-anaconda-upload -c PSLmodels --python 3.7"
cmd /c conda build %OPTIONS% .
echo "INSTALL..."
:: install local conda package
cmd /c conda install --yes -c PSLmodels taxcalc
cmd /c conda install --yes -c local biztax=0.0.0
echo "CLEANUP..."
:: clean-up intermediate build files after package build
cmd /c conda build purge
echo "FINISHED ---"
exit 0
