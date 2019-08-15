import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.domesticmne import DomesticMNE
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

    def __init__(self, btax_params, revenues, deductions,
                 credit, dmne=None,
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
        if isinstance(revenues, pd.DataFrame):
            self.revenues = revenues
        else:
            raise ValueError('revenues must be in DataFrame')
        if isinstance(deductions, pd.DataFrame):
            self.deductions = deductions
        else:
            raise ValueError('deductions must be in DataFrame')
        if isinstance(credit, pd.DataFrame):
            self.credits = credit
        else:
            raise ValueError('credits must be in DataFrame')
        if dmne is None:
            # Note: Don't do this in general
            self.dmne = DomesticMNE(self.btax_params)
            self.dmne.calc_all()
        elif isinstance(dmne, DomesticMNE):
            self.dmne = dmne
        else:
            raise ValueError('dmne must be a DomesticMNE object')
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
        # Prepare unmodeled components of tax return
        self.revenues['total'] = (self.revenues['receipts']
                                  + self.revenues['rent']
                                  + self.revenues['royalties']
                                  + self.revenues['capgains']
                                  + (self.revenues['domestic_divs'] *
                                     self.btax_params['domestic_dividend_inclusion'])
                                  + self.revenues['other']
                                  + self.dmne.dmne_results['foreign_taxinc'])
        # self.revenues.to_csv('revenues.csv')
        self.deductions['total'] = (self.deductions['cogs']
                                    + self.deductions['execcomp']
                                    + self.deductions['wages']
                                    + self.deductions['repairs']
                                    + self.deductions['baddebt']
                                    + self.deductions['rent']
                                    + self.deductions['statelocaltax']
                                    + self.deductions['charity']
                                    + self.deductions['amortization']
                                    + self.deductions['depletion']
                                    + self.deductions['advertising']
                                    + self.deductions['pensions']
                                    + self.deductions['benefits']
                                    + self.deductions['nol']
                                    + self.deductions['other'])
        # self.deductions.to_csv('deductions.csv')
        combined = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                 'ebitda': (self.revenues['total'] -
                                            self.deductions['total'])})
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

    def update_earnings(self, dearnings):
        """
        Updates the earnings DataFrame associated with the tax return.
        """
        assert len(dearnings) == NUM_YEARS
        fearnings = np.asarray(self.dmne.dmne_results['foreign_taxinc'])
        self.combined_return['ebitda'] = dearnings + fearnings

    def calcSec199(self):
        """
        Calculates section 199 deduction.
        """
        # Extract relevant parmeters
        s199_hclist = np.array(self.btax_params['sec199_hc'])
        sec199_base = np.asarray(self.deductions['sec199'])
        sec199_res = sec199_base * (1. - s199_hclist)
        self.combined_return['sec199'] = sec199_res

    def calcInitialTax(self):
        """
        Calculates taxable income and tax before credits.
        """
        netinc1 = (self.combined_return['ebitda'] -
                   self.combined_return['taxDep'] -
                   self.combined_return['nid'] -
                   self.combined_return['sec199'])
        self.combined_return['taxinc'] = np.maximum(netinc1, 0.)
        self.combined_return['tau'] = self.btax_params['tau_c']
        self.combined_return['taxbc'] = (self.combined_return['taxinc'] *
                                         self.combined_return['tau'])

    def calcFTC(self):
        """
        Gets foreign tax credit from DomesticMNE
        """
        self.combined_return['ftc'] = self.dmne.dmne_results['ftc']

    def calcAMT(self):
        """
        Calculates the AMT revenue and PYMTC for [START_YEAR, END_YEAR]
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
        A = np.zeros(NUM_YEARS)
        P = np.zeros(NUM_YEARS)
        stockA = np.zeros(NUM_YEARS + 1)
        stockN = np.zeros(NUM_YEARS + 1)
        stockA[0] = ((self.data.trans_amt1 * self.data.userate_pymtc +
                     self.data.trans_amt2 * (1 - self.data.userate_pymtc)) /
                     (1 - self.data.trans_amt1) * self.data.stock2014)
        stockN[0] = self.data.stock2014 - stockN[0]
        stockN[0] = ((1 - self.data.trans_amt1) /
                     (1 - self.data.trans_amt1 +
                     self.data.trans_amt1 * self.data.userate_pymtc +
                     self.data.trans_amt2 * (1 - self.data.userate_pymtc))
                     * self.data.stock2014)
        stockA[0] = self.data.stock2014 - stockN[0]
        for iyr in range(NUM_YEARS):
            # Calculate AMT
            if amt_rates[iyr] == 0.:
                # If no AMT
                A[iyr] = 0.
                frac_amt = 0.
            elif ctax_rates[iyr] <= amt_rates[iyr]:
                # If AMT rate exceeds regular rate (all subject to AMT)
                A[iyr] = ((amt_rates[iyr] - ctax_rates[iyr]
                           + amt_rates[iyr] / self.data.param_amt)
                          * taxinc[iyr])
                frac_amt = 0.999
            else:
                A[iyr] = (amt_rates[iyr] / self.data.param_amt *
                          np.exp(-self.data.param_amt
                                 * (ctax_rates[iyr] / amt_rates[iyr] - 1))
                          * taxinc[iyr])
                frac_amt = np.exp(-self.data.param_amt
                                  * (ctax_rates[iyr] / amt_rates[iyr] - 1))
            # Adjust transition params for change in AMT frequency
            alpha = max(0.0, min(1.0,
                                 (self.data.trans_amt1
                                  * (frac_amt / self.data.amt_frac) ** 0.5)))
            beta = (1 - alpha) * frac_amt / (1 - frac_amt)
            if pymtc_status[iyr] == 0:
                # No change from baseline
                userate = self.data.userate_pymtc
            elif pymtc_status[iyr] == 1:
                # PYMTC repealed
                userate = 0.0
            else:
                # PYMTC made fully refundable
                userate = 1.0
            P[iyr] = userate * stockN[iyr]
            stockA[iyr+1] = (alpha * (stockA[iyr] + A[iyr]) +
                             beta * (stockN[iyr] - P[iyr]))
            stockN[iyr+1] = ((1 - alpha) * (stockA[iyr] + A[iyr]) +
                             (1 - beta) * (stockN[iyr] - P[iyr]))
        # Rescale for any cross-sector shifting
        amt_final = A * self.data.rescale_corp
        pymtc_final = P * self.data.rescale_corp
        self.combined_return['amt'] = amt_final
        self.combined_return['pymtc'] = pymtc_final

    def calcTax(self):
        """
        Calculates final tax liability.
        """
        self.combined_return['gbc'] = self.credits['gbc']
        # Calculate final tax liability
        taxliab1 = (self.combined_return['taxbc'] +
                    self.combined_return['amt'] -
                    self.combined_return['ftc'] -
                    self.combined_return['pymtc'] -
                    self.combined_return['gbc'])
        self.combined_return['taxrev'] = np.maximum(taxliab1, 0.)

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
        tax = np.array(self.combined_return['taxrev'])
        return tax
