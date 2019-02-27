import numpy as np
import pandas as pd
import copy
from biztax.data import Data
from biztax.btaxmini import BtaxMini


class Response():
    """
    Constructor for the Response class. 
    This class manages all business responses to tax policy. Currently, these
    include:
        investment responses: to cost of capital and EATR
        debt responses: to tax shield from debt
        legal response: to tax differential across business forms
        
    Parameters:
        elast_dict: dict of response elasticities/semi-elasticities
        btax_params1: baseline policy parameters
        btax_params2: reform policy parameters
        
    Associated objects (results):
        investment_response: DataFrame of investment responses and MPKs
        debt_response: DataFrame of optimal borrowing responses
        rescale_corp & rescale_noncorp: rescaling measures from legal response
    
    WARNING: The legal response is not function in its current form!
    """
    
    def __init__(self, elast_dict, btax_params1, btax_params2):
        # Save elasticity dictionary
        self.elast_dict = elast_dict
        # Save policy parameters
        self.btax_params_base = copy.deepcopy(btax_params1)
        self.btax_params_ref = copy.deepcopy(btax_params2)
    
    def calc_inv_response(self):
        """
        Calculates the percent change in investment & marginal product of capital,
        for each asset type, for each year, corporate and noncorporate.
        firstyear: when the firm behavioral response takes effect
        """
        # Read in the underlying functions for the investment response
        maindata = copy.deepcopy(Data().assets_data())
        maindata.drop(['assets_c', 'assets_nc'], axis=1, inplace=True)
        # Extract relevant response parameters
        firstyear = self.elast_dict['first_year_response']
        elast_c = self.elast_dict['inv_usercost_c']
        elast_nc = self.elast_dict['inv_usercost_nc']
        selast_c = self.elast_dict['inv_eatr_c']
        selast_nc = self.elast_dict['inv_eatr_nc']
        mne_share_c = self.elast_dict['mne_share_c']
        mne_share_nc = self.elast_dict['mne_share_nc']
        # No responses for years before first_year_response
        for year in range(2014, firstyear):
            maindata['deltaIc' + str(year)] = 0.
            maindata['deltaInc' + str(year)] = 0.
            maindata['MPKc' + str(year)] = 0.
            maindata['MPKnc' + str(year)] = 0.
        # Calculate cost of capital and EATR for every year for baseline
        Btax_base = BtaxMini(self.btax_params_base)
        results_base = Btax_base.run_btax_mini(range(firstyear, 2028))
        # Calculate cost of capital and EATR for every year for reform
        Btax_ref = BtaxMini(self.btax_params_ref)
        results_ref = Btax_ref.run_btax_mini(range(firstyear, 2028))
        # Compare results to produce the responses
        for year in range(firstyear, 2028):
            maindata['deltaIc' + str(year)] = ((results_ref['u_c' + str(year)] / results_base['u_c' + str(year)] - 1) * elast_c +
                                               (results_ref['eatr_c' + str(year)] - results_base['eatr_c' + str(year)]) * selast_c * mne_share_c)
            maindata['deltaInc' + str(year)] = ((results_ref['u_nc' + str(year)] / results_base['u_nc' + str(year)] - 1) * elast_nc +
                                                (results_ref['eatr_nc' + str(year)] - results_base['eatr_nc' + str(year)]) * selast_nc * mne_share_nc)
            maindata['MPKc' + str(year)] = (results_ref['u_c' + str(year)] + results_base['u_c' + str(year)]) / 2.0
            maindata['MPKnc' + str(year)] = (results_ref['u_nc' + str(year)] + results_base['u_nc' + str(year)]) / 2.0
        # Save the responses
        self.investment_response = copy.deepcopy(maindata)
    
    def calc_debt_response_corp(self):
        """
        Calculates the corporate debt response.
        """
        # Extract the information on haircuts
        nid_hcs = np.array(self.btax_params_ref['netIntPaid_corp_hc'])
        id_hc_years = np.array(self.btax_params_ref['newIntPaid_corp_hcyear'])
        id_hc_new = np.array(self.btax_params_ref['newIntPaid_corp_hc'])
        yearlist = np.array(range(2014,2028))
        id_hcs = np.where(id_hc_years >= yearlist, id_hc_new, 0.0)
        hclist = np.maximum(nid_hcs, id_hcs)
        elast_debt_list = np.where(yearlist >= self.elast_dict['first_year_response'],
                                   self.elast_dict['debt_taxshield_c'], 0.0)
        taxshield_base = self.btax_params_base['tau_c']
        taxshield_ref = np.asarray(self.btax_params_ref['tau_c']) * (1 - hclist)
        pctch_delta = elast_debt_list * (taxshield_ref / taxshield_base - 1)
        return pctch_delta
    
    def calc_debt_response_noncorp(self):
        """
        Calculates the noncorporate debt response
        """
        # Extract the information on haircuts
        id_hc_years = np.array(self.btax_params_ref['newIntPaid_noncorp_hcyear'])
        id_hc_new = np.array(self.btax_params_ref['newIntPaid_noncorp_hc'])
        yearlist = np.array(range(2014,2028))
        hclist = np.where(id_hc_years >= yearlist, id_hc_new, 0.0)
        elast_debt_list = np.where(yearlist >= self.elast_dict['first_year_response'],
                                   self.elast_dict['debt_taxshield_nc'], 0.0)
        taxshield_base = self.btax_params_base['tau_nc']
        taxshield_ref = self.btax_params_ref['tau_nc'] * (1 - hclist)
        pctch_delta = (taxshield_ref / taxshield_base - 1) * elast_debt_list
        return pctch_delta
    
    def calc_debt_responses(self):
        """
        Calls the functions to calculate the debt responses and saves them in
        a DataFrame.
        """
        debtresp_c = self.calc_debt_response_corp()
        debtresp_nc = self.calc_debt_response_noncorp()
        debtresp_df = pd.DataFrame({'year': range(2014,2028),
                                    'pchDelta_corp': debtresp_c,
                                    'pchDelta_noncorp': debtresp_nc})
        self.debt_response = debtresp_df
    
    def legal_response(self):
        """
        Reallocation of business activity between corporate and noncorporate
        sections, achieved by modifying the rescaling factors. For now,
        assuming identical tax bases.
        """
        self.rescale_corp = np.ones(14)
        self.rescale_noncorp = np.ones(14)
        """
        elast = self.elast_dict['legalform_ratediff']
        firstyear = self.elast_dict['first_year_response']
        elast_list = np.zeros(14)
        for i in range(14):
            if i + 2014 >= firstyear:
                elast_list[i] = elast
        tau_nc_base = self.btax_params_base['tau_nc']
        tau_c_base = self.btax_params_base['tau_c']
        tau_nc_ref = self.btax_params_ref['tau_nc']
        tau_c_ref = self.btax_params_ref['tau_c']
        tau_e_base = self.btax_params_base['tau_e']
        tau_e_ref = self.btax_params_ref['tau_e']
        taxterm_base = (tau_c_base + tau_e_base - tau_c_base * tau_e_base -
                        tau_nc_base)
        taxterm_ref = tau_c_ref + tau_e_ref - tau_c_ref * tau_e_ref - tau_nc_ref
        legalshift = elast_list * (taxterm_ref - taxterm_base)
        # business activity shares
        earnings_c = combined_base['ebitda']
        earnings_nc = earnings_base['ebitda']
        assets_c = capPath_base_corp['Kstock']
        assets_nc = capPath_base_noncorp['Kstock']
        debt_c = NID_base['debt']
        debt_nc = IntPaid_base_noncorp['debt']
        cshare_earnings = earnings_c / (earnings_c + earnings_nc)
        cshare_assets = assets_c / (assets_c + assets_nc)
        cshare_debt = debt_c / (debt_c + debt_nc)
        cshare_base = (cshare_earnings + cshare_assets + cshare_debt) / 3.0
        cshare_ref = cshare_base + legalshift
        scale_c = cshare_ref / cshare_base
        scale_nc = (1 - cshare_ref) / (1 - cshare_base)
        self.rescale_corp = scale_c
        self.rescale_noncorp = scale_nc
        """
    
    def calc_all(self):
        """
        Executes all response calculations
        """
        self.calc_inv_response()
        self.calc_debt_responses()
        self.legal_response()
