# This folder contains models for Indonesia. 

## Documentation for World Bank Models 

[Standard Model documentation](https://elibrary.worldbank.org/doi/10.1596/1813-9450-8965#:~:text=MFMod%20consists%20of%20individual%20country,(ii)%20simulate%20various%20policies.)
[Equation estimation and calibration](https://documents1.worldbank.org/curated/en/662391562848917501/pdf/Estimating-and-Calibrating-MFMod-A-Panel-Data-Approach-to-Identifying-the-Parameters-of-Data-Poor-Countries-in-the-World-Banks-Structural-Macro-Model.pdf)
[Climate change enhancements (Pakistan model)](https://documents1.worldbank.org/curated/en/747101632403308927/pdf/Climate-Modeling-for-Macroeconomic-Policy-A-Case-Study-for-Pakistan.pdf)
[Climate change enhancements (Jamaica model)](https://documents1.worldbank.org/curated/en/593351609776234361/pdf/Macroeconomic-Modeling-of-Managing-Hurricane-Damage-in-the-Caribbean-The-Case-of-Jamaica.pdf)

## World Bank models using ModelFlow
Detailed documentation for solving World Bank models using Model Flow [The World Bank's MFMod Framework
in Python with Modelflow]()


## Indonesia model

This folder contains a climate aware version of MFMod built in 2022.  The model includes a compete representation of the national incomes accounts (nominal and real; expenditure, production and income perspectives), the current and financial accounts of the balance of payments, fiscal accounts for the general government and green house gas emissions, economic damages from increased temperatures, changes in rainfall variability, flooding and sea-level rise.

In addition to the model file itself, the folder contains two Jupyter notebooks illustrating the model's use and some of its features.

The first illustrates how to implement and the results of a series of [standard macroeconomic shocks](StandardShocks.ipnyb), illustrating the impact on the economy of:

* a temporary one-year 1 percent increase in the monetary policy interest rate;
* a permanent one percent increase in total factor productivity;
* the impact of a range of economic stimulus measures:
    * a 1 percent of GDP decrease in indirect taxes
    * a 1 percent of GDP decrease in direct taxes
    * a 1 percent of GDP increase in goverment spending on goods and services
    * a 1 percent of GDP increase in goverment spending on investment goods
    * a 1 percent of GDP increase in goverment spending on transfers to households
* a permanent $20 increase in the price of crude oil
* a permanent 10 percent depreciation of the currency



The second presents the results from the imposition of [a tax on electricity](idn electricity tax  shock.ipynb)

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="idn oil price shock.ipynb" target="_blank">idn oil price shock</a>

