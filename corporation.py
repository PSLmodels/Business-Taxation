import numpy as np
import pandas as pd
import copy
from data import Data
from asset import Asset
from debt import Debt
from corptaxreturn import CorpTaxReturn
from response import Response



class Corporation():
    """
    Constructor for the Corporation class. 
    This contains both the real and tax information relevant to the 
    corporate income tax.
    """
    
    def __init__(self, btax_params):
        # Store policy parameter objects
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        # Create Data object
        self.data = Data()
    
    def create_asset(self):
        """
        Creates the Asset object for the Corporation.
        """
        self.asset = Asset(self.btax_params, corp=True, data=self.data)
        self.asset.calc_all()
    
    def create_debt(self):
        """
        Creates the Debt object for the Corporation. 
        Note: create_asset must have already been called
        """
        self.debt = Debt(self.btax_params, self.asset.get_forecast(),
                         data=self.data, corp=True)
        self.debt.calc_all()
    
    def create_earnings(self):
        """
        Creates the initial forecast for earnings. Static only.
        """
        earnings_forecast = np.asarray(self.data.gfactors['profit'])
        earnings2013 = np.asarray(self.data.historical_taxdata['ebitda13'])[-1]
        earnings_new = earnings_forecast[1:] / earnings_forecast[0] * earnings2013
        self.earnings = earnings_new
    
    def file_taxes(self):
        """
        Creates the CorpTaxReturn object.
        """
        self.taxreturn = CorpTaxReturn(self.btax_params, self.earnings,
                                       data=self.data, assets=self.asset,
                                       debts=self.debt)
        self.taxreturn.calc_all()
    
    def real_activity(self):
        """
        Produces a DataFrame of the corporation's real activity.
        Real measures are:
            Capital stock
            Investment
            Depreciation (economic)
            Net debt
            Net interest paid
            Earnings
            Tax liability
            Net income
            Cash flow
        """
        real_results = pd.DataFrame({'year': range(2014,2028),
                                     'Earnings': self.earnings})
        real_results['Kstock'] = self.asset.get_forecast()
        real_results['Inv'] = self.asset.get_investment()
        real_results['Depr'] = self.asset.get_truedep()
        real_results['Debt'] = self.debt.get_debt()
        real_results['NIP'] = self.debt.get_nip()
        real_results['Tax'] = self.taxreturn.get_tax()
        real_results['NetInc'] = real_results['Earnings'] - real_results['Depr'] - real_results['NIP'] - real_results['Tax']
        real_results['CashFlow'] = real_results['Earnings'] - real_results['Inv'] - real_results['Tax']
        self.real_results = real_results
    
    def calc_static(self):
        """
        Runs the static calculations.
        """
        self.create_asset()
        self.create_earnings()
        self.create_debt()
        self.file_taxes()
        self.real_activity()
    
    def update_legal(self, responses):
        """
        Updates the rescale_corp and rescale_noncorp associated with each
        Data associated with each object.
        """
        self.data.update_rescaling(responses.rescale_corp, responses.rescale_noncorp)
        self.asset.data.update_rescaling(responses.rescale_corp, responses.rescale_noncorp)
    
    def update_investment(self, responses):
        """
        Updates the Asset object to include investment response.
        """
        # First, save the capital stock by asset type and year (for earnings)
        self.old_capital_history = copy.deepcopy(self.asset.capital_history)
        self.asset.update_response(responses.investment_response)
        self.asset.calc_all()
    
    def update_earnings(self, responses):
        """
        Recalculates earnings using the old capital stock by asset type, the
        new capital stock by asset type (based on the investment response),
        and the marginal product of capital.
        """
        Kstock_base = copy.deepcopy(self.old_capital_history)
        Kstock_ref = copy.deepcopy(self.asset.capital_history)
        deltaK = Kstock_ref - Kstock_base
        changeEarnings = np.zeros((96, 14))
        for j in range(14): # for each year
            mpk = np.array(responses.investment_response['MPKc' + str(j + 2014)])
            for i in range(96): # by asset
                changeEarnings[i,j] = deltaK[i,j] * mpk[i] * self.data.adjfactor_dep_corp
        deltaE = np.zeros(14)
        for j in range(14):
            deltaE[j] = changeEarnings[:, j].sum()
        self.earnings = (self.earnings + deltaE) * self.data.rescale_corp
    
    def update_debt(self, responses):
        """
        Replaces the Debt object to use the new asset forecast and Data
        """
        pctch_delta = np.array(responses.debt_response['pchDelta_corp'])
        self.debt = Debt(self.btax_params, self.asset.get_forecast(),
                         data=self.data, response=pctch_delta, corp=True)
        self.debt.calc_all()
    
    def apply_responses(self, responses):
        """
        Updates Data, Asset, earnings, Debt and CorpTaxReturn to include 
        responses. Then calc_all() for each object.
        """
        assert isinstance(responses, Response)
        self.update_legal(responses)
        self.update_investment(responses)
        self.update_earnings(responses)
        self.update_debt(responses)
        self.file_taxes()
        self.real_activity()
        
    def get_netinc(self):
        """
        Returns an array of the corporation's net income (after-tax).
        """
        netinc = np.array(self.real_results['NetInc'])
        return netinc
    
    def get_taxrev(self):
        """
        Returns an array of the corporation's tax liability.
        """
        taxrev = np.array(self.real_results['Tax'])
        return taxrev
    
        