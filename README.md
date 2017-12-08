# BRC
## About BRC
BRC (short for Business Tax Revenue Calculator) is a model to evaluate the effects of business tax policy on federal tax revenue. BRC uses IRS data, data on business assets and debt, and microdata on individual tax filers to compute changes in tax revenue. In modeling business capital, BRC relies on data from [B-Tax](https://github.com/open-source-economics/B-Tax), an open source model for marginal effective tax rates on new investments. When distributing the changes in corporate business activity to owners of capital, BRC relies on [Tax-Calculator](https://github.com/open-source-economics/tax-calculator), another open source model of federal income and payroll taxes. BRC is written in Python, an interpreted language that can execute on Windows, Mac, or Linux.

## Disclaimer
This model is in a preliminary state and currently under development. The model components and the results will change as the model improves. Therefore, there is no guarantee of accurary. As of this version, the code should not be used for publications, journal articles or research purposes. 

## Set-up Instructions
External dependencies:
 - taxcalc (Tax-Calculator)
 - Public use file
Note that although this model uses data produced by B-Tax, BTax is not a dependency. 

 - First, set up Python and GitHub. See the [instructions](http://taxcalc.readthedocs.io/en/latest/contributor_guide.html) for setting up Tax-Calculator. 
 - Clone this repo (or the one forked to your account). Navigate to the cloned repo, and enter the following commands:
   - `git remote add upstream https://github.com/open-source-economics/btc.git`
   - `conda env create`
 - In the `BRC` folder, add `taxcalc` and `puf.csv`. 
 - To run BRC, see the example code in `combined_corporate_model.ipynb`. 

## Citing BRC
BRC (Version 0.0.0)[Source code], https://github.com/open-source-economics/BRC