import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS, HISTORY_START
from biztax.data import Data


class Debt():
    """
    Constructor for the Debt class.
    This class includes several objects related to debt:
        debt history:
            record from 1960 - END_YEAR of debt-related measures:
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
        btax_params: DataFrame of business tax policy parameters
        asset_forecast: list of nonfinancial asset amounts
        response: array of percent changes in optimal debt-asset ratios
        eta: debt retirement rate
    """

    def __init__(self, btax_params, asset_forecast,
                 data=None, response=None, eta=0.4,
                 corp=True, industry='ALL'):
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
        if response is None:
            self.response = np.zeros(NUM_YEARS)
        else:
            if len(response) == NUM_YEARS:
                self.response = response
            else:
                raise ValueError('Wrong response')
        if corp:
            self.delta = (np.array(self.data.debt_forecast['f_c_l'])
                          * (1 + self.response))
        else:
            self.delta = (np.array(self.data.debt_forecast['f_nc_l'])
                          * (1 + self.response))
        if len(asset_forecast) == NUM_YEARS:
            self.asset_forecast = asset_forecast
        else:
            raise ValueError('Wrong length for asset forecast')
        if eta >= 0 and eta <= 1:
            self.eta = eta
        else:
            raise ValueError('Value of eta inappropriate')

    def get_haircuts(self):
        if self.corp:
            hc_id_old_years = np.array(self.btax_params['oldIntPaid_corp_hcyear'])
            hc_id_olds = np.array(self.btax_params['oldIntPaid_corp_hc'])
            hc_id_new_years = np.array(self.btax_params['newIntPaid_corp_hcyear'])
            hc_id_news = np.array(self.btax_params['newIntPaid_corp_hc'])
        else:
            hc_id_old_years = np.array(self.btax_params['oldIntPaid_noncorp_hcyear'])
            hc_id_olds = np.array(self.btax_params['oldIntPaid_noncorp_hc'])
            hc_id_new_years = np.array(self.btax_params['newIntPaid_noncorp_hcyear'])
            hc_id_news = np.array(self.btax_params['newIntPaid_noncorp_hc'])
        haircuts = {}
        haircuts['id_hc_oldyear'] = hc_id_old_years
        haircuts['id_hc_old'] = hc_id_olds
        haircuts['id_hc_newyear'] = hc_id_new_years
        haircuts['id_hc_new'] = hc_id_news
        self.haircuts = haircuts

    def build_level_history(self):
        """
        Constructs the debt level history from 1960 to 2016.
        """
        # Grab historical records for 1960-2014
        if self.corp:
            At = self.data.debt_data['At_c'].tolist()
            An = self.data.debt_data['An_c'].tolist()
            L = self.data.debt_data['L_c'].tolist()
        else:
            At = [0] * (START_YEAR - HISTORY_START + 1)
            An = [0] * (START_YEAR - HISTORY_START + 1)
            L = self.data.debt_data['L_nc'].tolist()
        D = [L[i] - At[i] - An[i] for i in range(len(L))]
        i_t = self.data.debt_data['i_t'].tolist()
        i_pr = self.data.debt_data['i_pr'].tolist()
        # Extend for 2015-2027
        At.extend(At[START_YEAR-HISTORY_START] * self.asset_forecast[1:] / self.asset_forecast[0])
        An.extend(An[START_YEAR-HISTORY_START] * self.asset_forecast[1:] / self.asset_forecast[0])
        D.extend(D[54] * self.asset_forecast[1:] / self.asset_forecast[0]
                 * self.delta[1:] / self.delta[0])
        L = [D[i] + At[i] + An[i] for i in range(len(D))]
        i_t.extend(self.data.debt_forecast['i_t'][1:])
        i_pr.extend([i_pr[START_YEAR-HISTORY_START]] * (NUM_YEARS-1))
        # Save level histories
        self.net_debt_history = D
        self.debt_asset_history = At
        self.muni_asset_history = An
        self.debt_liab_history = L
        self.i_a = i_t
        self.i_l = i_t + i_pr

    def build_flow_history(self):
        """
        Constructs originations.
        """
        O = np.zeros(END_YEAR - HISTORY_START + 1)
        for i in range(1, END_YEAR - HISTORY_START + 1):
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
            At = copy.deepcopy(self.debt_asset_history)
            An = copy.deepcopy(self.muni_asset_history)
            L_opt = copy.deepcopy(self.debt_liab_history)
            L = np.zeros(END_YEAR - HISTORY_START + 1)
            L[0] = L_opt[0]
            O = np.zeros(END_YEAR - HISTORY_START + 1)
            for i in range(1, END_YEAR - HISTORY_START + 1):
                O[i] = max(L_opt[i] - L[i-1] * (1 - self.eta), 0.)
                L[i] = L[i-1] * (1 - self.eta) + O[i]
            self.debt_liab_history = L
            self.originations = O
            self.net_debt_history = L - At - An

    def calc_real_interest(self):
        """
        Calculates interest income and interest paid.
        """
        self.int_income = (np.array(self.debt_asset_history)
                           * np.array(self.i_a))
        self.muni_income = (np.array(self.muni_asset_history)
                            * np.array(self.i_a))
        int_expense = np.zeros(END_YEAR - HISTORY_START + 1)
        for i in range(1, END_YEAR - HISTORY_START + 1):
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
        int_expded = np.zeros(END_YEAR - HISTORY_START + 1)
        # Calculations for years before the budget window
        for i in range(1, 54):
            for j in range(i+1):
                int_expded[i] += (self.originations[j] *
                                  (1 - self.eta)**(i - j - 1) * self.i_l[j])
        # Calculations during the budget window
        for i in range(START_YEAR-HISTORY_START, END_YEAR - HISTORY_START + 1):
            for j in range(i+1):
                hctouse = 0.0
                if j + HISTORY_START < self.haircuts['id_hc_oldyear'][i-(START_YEAR-HISTORY_START)]:
                    # If originated before "old" haircut, apply haircut
                    hctouse = self.haircuts['id_hc_old'][i-54]
                if j + HISTORY_START >= self.haircuts['id_hc_newyear'][i-(START_YEAR-HISTORY_START)]:
                    # If originated after "new" haircut, apply haircut
                    hctouse = max(hctouse, self.haircuts['id_hc_new'][i-(START_YEAR-HISTORY_START)])
                int_expded[i] += (self.originations[j] * (1 - self.eta)**(i-j)
                                  * self.i_l[j] * (1 - hctouse))
        self.int_expded = int_expded

    def build_interest_path(self):
        """
        Builds a DataFrame wit relevant debt information for the budget window:
            debt: net debt totals
            nip: net interest paid
            nid: net interest deduction

        WARNING: May need to include rescale_corp and rescale_noncorp
        """
        debt = np.array(self.net_debt_history[START_YEAR-HISTORY_START:])
        nip = np.array(self.int_expense[START_YEAR-HISTORY_START:]
                       - self.int_income[START_YEAR-HISTORY_START:] - self.muni_income[START_YEAR-HISTORY_START:])
        nid = np.array(self.int_expded[START_YEAR-HISTORY_START:]
                       - self.int_income[START_YEAR-HISTORY_START:])
        NID_results = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                    'nid': nid,
                                    'nip': nip,
                                    'debt': debt})
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
        Returns the net interest deductions for [START_YEAR, END_YEAR]
        """
        nid = np.array(self.interest_path['nid'])
        return nid

    def get_intDed(self):
        """
        Returns deductible interest expense.
        """
        int1 = self.int_expded[START_YEAR-HISTORY_START:]
        return int1

    def get_intInc(self):
        """
        Returns interest income (excluding on muni bonds).
        """
        int1 = self.int_income[START_YEAR-HISTORY_START:]
        return int1

    def get_muniInc(self):
        """
        Returns interest income from municipal bonds.
        """
        int1 = self.muni_income[START_YEAR-HISTORY_START:]
        return int1

    def get_intPaid(self):
        """
        Returns interest paid.
        """
        int1 = self.int_expense[START_YEAR-HISTORY_START:]
        return int1

    def get_nip(self):
        """
        Returns the net interest paid for [START_YEAR, END_YEAR]
        """
        nip = np.array(self.interest_path['nip'])
        return nip

    def get_debt(self):
        """
        Returns the net debtfor [START_YEAR, END_YEAR]
        """
        debt = np.array(self.interest_path['debt'])
        return debt
