# Business-Taxation
## About Business-Taxation
Business-Taxation is a model to evaluate the effects of business tax policy on federal tax revenue. Business-Taxation uses IRS data, data on business assets and debt, and microdata on individual tax filers to compute changes in tax revenue. In modeling business capital, Business-Taxation relies on data from [B-Tax](https://github.com/PSLmodels/B-Tax), an open source model for marginal effective tax rates on new investments. When distributing the changes in corporate business activity to owners of capital, Business-Taxation relies on [Tax-Calculator](https://github.com/open-source-economics/tax-calculator), another open source model of federal income and payroll taxes. Business-Taxation is written in Python, an interpreted language that can execute on Windows, Mac, or Linux.

## Disclaimer
This model is in a preliminary state and currently under development. The model components and the results will change as the model improves. Therefore, there is no guarantee of accurary. As of this version, the code should not be used for publications, journal articles or research purposes. 

## Set-up Instructions
External dependencies:
 - taxcalc (Tax-Calculator)
 - Public use file

Note that although this model uses data produced by B-Tax, btax is not a dependency. 

Instructions:

 - First, set up Python and GitHub. See the [instructions](http://taxcalc.readthedocs.io/en/latest/contributor_guide.html) for setting up Tax-Calculator. 
 - Clone this repo (or the one forked to your account). Navigate to the cloned repo, and enter the following commands:
   - `git remote add upstream https://github.com/PSLmodels/Business-Taxation.git`
   - `conda env create`
 - In the `Business-Taxation` folder, add `puf.csv`. Check that taxcalc is installed as a package. 
 - To run Business-Taxation, see the example code in `example.py`. 

## Current status
Business-Taxation is undergoing a major refactoring to improve it and make it PSL-compliant. Currently, the static analysis can be run, as well as the analysis using the investment and debt responses.

## Citing BRC
BRC (Version 0.0.0)[Source code], https://github.com/PSLmodels/Business-Taxation