import numpy as np
import pandas as pd
import copy
from data import Data

class Debt():
    """
    Constructor for the Debt class.
    This class includes several objects related to debt:
        debt history:
            record from 1960 - 2027 of debt-related measures:
                K_fa: assets (financial accounts)
                A: debt assets
                L: debt liabilities
                i_t: T-bond interest rates
                i_pr: premium over T-bond rates
        calculations within the budget window:
            debt_totals: aggregate debt amounts
            interest_real: interest received and paid
            interest_tax: taxable interest income and interest deductions
    
    Parameters:
        corp: True for corporate, False for noncorporate
        btax_params: dict of business tax policy parameters
        asset_forecast: list of nonfinancial asset amounts
        response: list of percent changes in optimal debt-asset ratios
        eta: debt retirement rate
    """
    
    def __init__(self, btax_params, asset_forecast,
                 data=None, response=None, eta = 0.4, corp=True):
        # Create an associated Data object
        if isinstance(data, Data):
            self.data = data
        else:
            self.data = Data()
        if isinstance(corp, bool):
            self.corp = corp
        else:
            raise ValueError('corp must be True or False')
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        if response is not None:
            if len(response) == 14:
                self.response = response
            else:
                raise ValueError('Wrong response')
        else:
            self.response = np.zeros(14)
        if corp:
            self.delta = np.array(self.data.econ_defaults['f_c']) * (1 + self.response)
        else:
            self.delta = np.array(self.data.econ_defaults['f_nc']) * (1 + self.response)
        if len(asset_forecast) == 14:
            self.asset_forecast = asset_forecast
        else:
            raise ValueError('Wrong length for asset forecast')
        if eta >= 0 and eta <= 1:
            self.eta = eta
        else:
            raise ValueError('Value of eta inappropriate')
    
    def get_haircuts(self):
        if self.corp:
            hc_nids = np.array(self.btax_params['netIntPaid_corp_hc'])
            hc_id_old_years = np.array(self.btax_params['oldIntPaid_corp_hcyear'])
            hc_id_olds = np.array(self.btax_params['oldIntPaid_corp_hc'])
            hc_id_new_years = np.array(self.btax_params['newIntPaid_corp_hcyear'])
            hc_id_news = np.array(self.btax_params['newIntPaid_corp_hc'])
        else:
            hc_nids =np.zeros(14)
            hc_id_old_years = np.array(self.btax_params['oldIntPaid_noncorp_hcyear'])
            hc_id_olds = np.array(self.btax_params['oldIntPaid_noncorp_hc'])
            hc_id_new_years = np.array(self.btax_params['newIntPaid_noncorp_hcyear'])
            hc_id_news = np.array(self.btax_params['newIntPaid_noncorp_hc'])
        haircuts = {}
        haircuts['nid_hc']= hc_nids
        haircuts['id_hc_oldyear'] = hc_id_old_years
        haircuts['id_hc_old'] = hc_id_olds
        haircuts['id_hc_newyear'] = hc_id_new_years
        haircuts['id_hc_new'] = hc_id_news
        self.haircuts = haircuts
    
    def build_level_history(self):
        """
        Constructs the debt level history from 1960 to 2016. 
        """
        # Grab historical records for 1960-2016
        if self.corp:
            K_fa = self.data.debt_data_corp['Kfa'][:57].tolist()
            A = self.data.debt_data_corp['A'][:57].tolist()
            L = self.data.debt_data_corp['L'][:57].tolist()
            D = [L[i] - A[i] for i in range(len(L))]
            i_t = self.data.debt_data_corp['i_t'].tolist()
            i_pr = self.data.debt_data_corp['i_pr'].tolist()
        else:
            K_fa = self.data.debt_data_noncorp['Kfa'][:57].tolist()
            A = [0] * 57
            L = self.data.debt_data_noncorp['L'][:57].tolist()
            D = [L[i] - A[i] for i in range(len(L))]
            i_t = self.data.debt_data_noncorp['i_t'].tolist()
            i_pr = self.data.debt_data_noncorp['i_pr'].tolist()
        # Extend for 2017-2027
        for i in range(57, 68):
            K_fa.append(K_fa[56] * self.asset_forecast[i-54] /
                        self.asset_forecast[2])
            A.append(A[56] * K_fa[i] / K_fa[56])
            D.append(D[56] * K_fa[i] / K_fa[56] * self.delta[i-54] / self.delta[2])
            L.append(D[i] + A[i])
        # Save level histories
        self.net_debt_history = D
        self.debt_asset_history = A
        self.debt_liab_history = L
        self.i_a = [x / 100. for x in i_t]
        self.i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    
    def build_flow_history(self):
        """
        Constructs originations. 
        """
        O = np.zeros(68)
        for i in range(1,68):
            O[i] = (self.debt_liab_history[i] -
                    self.debt_liab_history[i-1] * (1 - self.eta))
        self.originations = O
    
    def constrain_history(self):
        """
        Recalculates level and flow histories subject to the constraint that
        originations must be nonnegative. 
        
        Note: This is not binding in general, only in the cases of either
              large changes to the optimal debt-to-asset ratio or for very low
              values of eta.
        """
        if min(self.originations) < 0.:
            A = copy.deepcopy(self.debt_asset_history)
            L_opt = copy.deepcopy(self.debt_liab_history)
            L = np.zeros(68)
            L[0] = L_opt[0]
            O = np.zeros(68)
            for i in range(1,68):
                O[i] = max(L_opt[i] - L[i-1] * (1 - self.eta), 0.)
                L[i] = L[i-1] * (1 - self.eta) + O[i]
            self.debt_liab_history = L
            self.originations = O
            self.net_debt_history = L + A
    
    def calc_real_interest(self):
        """
        Calculates interest income, interest paid and net interest paid.
        """
        self.int_income = np.array(self.debt_asset_history) * np.array(self.i_a)
        int_expense = np.zeros(68)
        for i in range(1, 68):
            for j in range(i+1):
                int_expense[i] += (self.originations[j] *
                                   (1 - self.eta)**(i - j) * self.i_l[j])
        self.int_expense = int_expense
    
    def calc_tax_interest(self):
        """
        Calculates taxable interest income, deductible interest and the
        net interest deduction based on tax law.
        """
        int_income = copy.deepcopy(self.int_income)
        int_expded = np.zeros(68)
        # Calculations for years before the budget window
        for i in range(1, 54):
            for j in range(i+1):
                int_expded[i] += (self.originations[j] *
                                  (1 - self.eta)**(i - j - 1) * self.i_l[j])
        # Calculations during the budget window
        for i in range(54, 68):
            for j in range(i+1):
                hctouse = 0.0
                if j + 1960 < self.haircuts['id_hc_oldyear'][i-54]:
                    # If originated before "old" haircut, apply haircut
                    hctouse = self.haircuts['id_hc_old'][i-54]
                if j + 1960 >= self.haircuts['id_hc_newyear'][i-54]:
                    # If originated after "new" haircut, apply haircut
                    hctouse = max(hctouse, self.haircuts['id_hc_new'][i-54])
                int_expded[i] += (self.originations[j] * (1 - self.eta)**(i-j) *
                                  self.i_l[j] * (1 - hctouse))
        NID_gross = int_expded - int_income
        # Get (contemporary) NID haircut
        nid_hc = np.zeros(68)
        nid_hc[54:68] = self.haircuts['nid_hc']
        NID = NID_gross * (1 - nid_hc)
        self.int_expded = int_expded
        self.NID = NID
    
    def build_interest_path(self):
        """
        Builds a DataFrame wit relevant debt information for the budget window:
            debt: net debt totals
            nip: net interest paid
            nid: net interest deduction
            
        WARNING: May need to include rescale_corp and rescale_noncorp
        """
        if self.corp:
            adjfactor = self.data.adjfactor_int_corp
        else:
            adjfactor = self.data.adjfactor_int_noncorp
        debt = np.array(self.net_debt_history[54:68]) * adjfactor
        nip = np.array(self.int_expense[54:68] - self.int_income[54:68]) * adjfactor
        nid = np.array(self.int_expded[54:68] - self.int_income[54:68]) * adjfactor
        NID_results = pd.DataFrame({'year': range(2014, 2028), 'nid': nid,
                                    'nip': nip, 'debt': debt})
        self.interest_path = NID_results
    
    def calc_all(self):
        """
        Executes all calculations for Debt object.
        """
        self.get_haircuts()
        self.build_level_history()
        self.build_flow_history()
        self.constrain_history()
        self.calc_real_interest()
        self.calc_tax_interest()
        self.build_interest_path()
        return None
    
    def get_nid(self):
        """
        Returns the net interest deductions for 2014-2027
        """
        nid = np.array(self.interest_path['nid'])
        return nid
    
    def get_nip(self):
        """
        Returns the net interest paid for 2014-2027
        """
        nip = np.array(self.interest_path['nip'])
        return nip
    
    def get_debt(self):
        """
        Returns the net debtfor 2014-2027
        """
        debt1 = np.array(self.interest_path['debt'])
        return debt1
    
    
    