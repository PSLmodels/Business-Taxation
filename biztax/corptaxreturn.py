import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.asset import Asset
from biztax.debt import Debt


class CorpTaxReturn():
    """
    Constructor for the CorpTaxReturn object. 
    This class includes objects relevant to the calculation of 
    corporate income tax liability:
        assets: an associated Asset object
        debts: an associated debt object
        combined_return: a DataFrame with tax calculations for each year
    
    Parameters:
        btax_params: dict of business tax policy parameters
        assets: Asset object for the corporation
        debts: Debt object for the corporation
        earnings: list or array of earnings for each year in the budget window
    """
    
    def __init__(self, btax_params, earnings,
                 data=None, assets=None, debts=None):
        # Create an associated Data object
        if isinstance(data, Data):
            self.data = data
        else:
            self.data = Data()
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        if assets is not None:
            if isinstance(assets, Asset):
                self.assets = assets
            else:
                raise ValueError('assets must be Asset object')
        else:
            self.assets = Asset(btax_params)
            self.assets.calc_all()
        if debts is not None:
            if isinstance(debts, Debt):
                self.debts = debts
            else:
                raise ValueError('debts must be Debt object')
        else:
            assets_forecast = self.assets.get_forecast()
            self.debts = Debt(btax_params, assets_forecast)
            self.debts.calc_all()
        # Use earnings to create DataFrame for results
        assert len(earnings) == 14
        combined = pd.DataFrame({'year': range(2014,2028), 'ebitda': earnings})
        # Add tax depreciation and net interest deductions
        combined['taxDep'] = self.assets.get_taxdep()
        combined['nid'] = self.debts.get_nid()
        self.combined_return = combined
    
    def update_assets(self, assets):
        """
        Updates the Asset object associated with the tax return.
        """
        if isinstance(assets, Asset):
            self.assets = assets
        else:
            raise ValueError('assets must be Asset object')
    
    def update_debts(self, debts):
        """
        Updates the Debt object associated with the tax return.
        """
        if isinstance(debts, Debt):
            self.debts = debts
        else:
            raise ValueError('debts must be Debt object')
    
    def update_earnings(self, earnings):
        """
        Updates the earnings DataFrame associated with the tax return.
        """
        assert len(earnings) == 14
        self.combined_return['ebitda'] = earnings
    
    def calcSec199(self):
        """
        Calculates section 199 deduction.
        """
        # Extract relevant parmeters
        s199_hclist = np.array(self.btax_params['sec199_hc'])
        profit = np.asarray(self.data.gfactors['profit_d'])
        sec199_res = np.zeros(14)
        sec199_2013 = np.asarray(self.data.historical_taxdata['sec199'])[-1]
        for i in range(14):
            sec199_res[i] = profit[i+1] / profit[0] * sec199_2013 * (1 - s199_hclist[i])
        self.combined_return['sec199'] = sec199_res
    
    def calcInitialTax(self):
        """
        Calculates taxable income and tax before credits.
        """
        self.combined_return['taxinc'] = (self.combined_return['ebitda'] -
                                          self.combined_return['taxDep'] -
                                          self.combined_return['nid'] -
                                          self.combined_return['sec199'])
        self.combined_return['tau'] = self.btax_params['tau_c']
        self.combined_return['taxbc'] = (self.combined_return['taxinc'] *
                                         self.combined_return['tau'])
    
    def calcFTC(self):
        """
        Calculates foreign tax credit for 2014-2027.
        """
        hclist = np.array(self.btax_params['ftc_hc'])
        def calcWAvgTaxRate(year):
            """
            Calculates the weighted average statutory corporate tax rate
            in all OECD countries in a given year.
            """
            assert year in range(1995, 2028)
            year = min(year, 2016)
            gdp_list = np.asarray(self.data.ftc_gdp_data[str(year)])
            taxrate_list = np.asarray(self.data.ftc_taxrates_data[str(year)])
            # remove observations with missing data
            taxrate_list2 = np.where(np.isnan(taxrate_list), 0, taxrate_list)
            gdp_list2 = np.where(np.isnan(taxrate_list), 0, gdp_list)
            avgrate = sum(taxrate_list2 * gdp_list2) / sum(gdp_list2)
            return avgrate
        # Get foreign profits forecast
        profits = np.asarray(self.data.ftc_other_data['C_total'][19:])
        profits_d = np.asarray(self.data.ftc_other_data['C_domestic'][19:])
        tax_f = np.zeros(14)
        for i in range(14):
            tax_f[i] = calcWAvgTaxRate(i + 2014)
        ftc_final = ((profits - profits_d) * tax_f / 100. *
                     self.data.adjfactor_ftc_corp *
                     (1 - hclist)) * self.data.rescale_corp
        self.combined_return['ftc'] = ftc_final
    
    def calcAMT(self):
        """
        Calculates the AMT revenue and PYMTC for 2014-2027
        pymtc_status: 0 for no change, 1 for repeal, 2 for refundable
        """
        # Get relevant tax information
        taxinc = np.array(self.combined_return['taxinc'])
        amt_rates = np.array(self.btax_params['tau_amt'])
        ctax_rates = np.array(self.btax_params['tau_c'])
        pymtc_status = np.array(self.btax_params['pymtc_status'])
        # Check values for PYMTC status
        for x in pymtc_status:
            assert x in [0, 1, 2]
        # Create empty arrays for AMT, PYMTC, and stocks (by status)
        A = np.zeros(14)
        P = np.zeros(14)
        stockA = np.zeros(15)
        stockN = np.zeros(15)
        stockA[0] = ((self.data.trans_amt1 * self.data.userate_pymtc + self.data.trans_amt2 *
                      (1 - self.data.userate_pymtc)) / (1 - self.data.trans_amt1) * self.data.stock2014)
        stockN[0] = self.data.stock2014 - stockN[0]
        stockN[0] = (1 - self.data.trans_amt1) / (1 - self.data.trans_amt1 + self.data.trans_amt1 *
                                                  self.data.userate_pymtc + self.data.trans_amt2 *
                                                  (1 - self.data.userate_pymtc)) * self.data.stock2014
        stockA[0] = self.data.stock2014 - stockN[0]
        for i in range(14):
            # Calculate AMT
            if amt_rates[i] == 0.:
                # If no AMT
                A[i] = 0.
                frac_amt = 0.
            elif ctax_rates[i] <= amt_rates[i]:
                # If AMT rate exceeds regular rate (all subject to AMT)
                A[i] = ((amt_rates[i] - ctax_rates[i] + amt_rates[i] / self.data.param_amt) *
                        taxinc[i])
                frac_amt = 0.999
            else:
                A[i] = (amt_rates[i] / self.data.param_amt *
                        np.exp(-self.data.param_amt * (ctax_rates[i] / amt_rates[i] - 1)) *
                        taxinc[i])
                frac_amt = np.exp(-self.data.param_amt * (ctax_rates[i] / amt_rates[i] - 1))
            # Adjust transition params for change in AMT frequency
            alpha = max(0.0, min(1.0, self.data.trans_amt1 * (frac_amt / self.data.amt_frac)**0.5))
            beta = (1 - alpha) * frac_amt / (1 - frac_amt)
            if pymtc_status[i] == 0:
                # No change from baseline
                userate = self.data.userate_pymtc
            elif pymtc_status[i] == 1:
                # PYMTC repealed
                userate = 0.0
            else:
                # PYMTC made fully refundable
                userate = 1.0
            P[i] = userate * stockN[i]
            stockA[i+1] = (alpha * (stockA[i] + A[i]) +
                           beta * (stockN[i] - P[i]))
            stockN[i+1] = ((1 - alpha) * (stockA[i] + A[i]) +
                           (1 - beta) * (stockN[i] - P[i]))
        # Rescale for any cross-sector shifting
        amt_final = A * self.data.rescale_corp
        pymtc_final = P * self.data.rescale_corp
        self.combined_return['amt'] = amt_final
        self.combined_return['pymtc'] = pymtc_final
    
    def calcTax(self):
        """
        Calculates final tax liability.
        """
        # Calculate general business credits
        profit = np.asarray(self.data.gfactors['profit_d'])
        gbc_2013 = np.asarray(self.data.historical_taxdata['gbc'])[-1]
        gbc_res = profit[1:] / profit[0] * gbc_2013
        self.combined_return['gbc'] = gbc_res
        # Calculate final tax liability
        self.combined_return['taxrev'] = (self.combined_return['taxbc'] +
                                          self.combined_return['amt'] -
                                          self.combined_return['ftc'] -
                                          self.combined_return['pymtc'] -
                                          self.combined_return['gbc'])
    
    def calc_all(self):
        """
        Executes all tax calculations.
        """
        self.calcSec199()
        self.calcInitialTax()
        self.calcFTC()
        self.calcAMT()
        self.calcTax()
    
    def getReturn(self):
        """
        Returns the tax return information
        """
        combined_result = copy.deepcopy(self.combined_return)
        return combined_result
    
    def get_tax(self):
        """
        Returns the total tax liability.
        """
        tax1 = np.array(self.combined_return['taxrev'])
        return tax1
    
    
    
