# BRC
## About BRC
BRC (short for Business Tax Revenue Calculator) is a model to evaluate the effects of business tax policy on federal tax revenue. BRC uses data of business assets and microdata on individual tax filers to compute changes in tax revenue. In modeling business capital, BRC relies on data from [B-Tax](https://github.com/open-source-economics/B-Tax), an open source model for marginal effective tax rates on new investments. When distributing the changes in corporate business activity to owners of capital, BRC relies on [Tax-Calculator](https://github.com/open-source-economics/tax-calculator), another open source model of federal income and payroll taxes. BRC is written in Python, an interpreted language that can execute on Windows, Mac, or Linux.

## Disclaimer
This model is in a preliminary state and currently under development. The model components and the results will change as the model improves. Therefore, there is no guarantee of accurary. As of this version, the code should not be used for publications, journal articles or research purposes. 

## Set-up Instructions
External dependencies:
 - taxcalc (Tax-Calculator)
 - btax (B-Tax)
 - Public use file

## Citing BRC
BRC (Version 0.0.0)[Source code], https://github.com/open-source-economics/BRC