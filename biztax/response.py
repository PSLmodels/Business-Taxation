"""
Business-Taxation Response class.
"""
import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.btaxmini import BtaxMini


class Response():
    """
    Constructor for the Response class.
    This class manages all business responses to tax policy.
    Currently, these include:
        investment responses: to cost of capital and EATR
        debt responses: to tax shield from debt
        repatriation responses: to change in tax penalty from repatriating
        legal response: to tax differential across business forms

    Parameters:
        none

    Associated objects (results):
        investment_response: DataFrame of investment responses and MPKs
        debt_response: DataFrame of optimal borrowing responses
        repatriation_response: DataFrame of repatriation responses
        rescale_corp & rescale_noncorp: rescaling measures from legal response

    WARNING: The legal response method is not in use!
    """

    DEFAULT_ELASTICITIES = {
        'inv_usercost_c': 0.0,
        'inv_usercost_nc': 0.0,
        'inv_eatr_c': 0.0,
        'inv_eatr_nc': 0.0,
        'mne_share_c': 0.0,
        'mne_share_nc': 0.0,
        'debt_taxshield_c': 0.0,
        'debt_taxshield_nc': 0.0,
        'reprate_inc': 0.0,
        'legalform_ratediff': 0.0,
        'first_year_response': 2017
    }

    def __init__(self):
        # Specify default elasticity values
        self.elasticities = Response.DEFAULT_ELASTICITIES
        # Set response results to None
        self.investment_response = None
        self.debt_response = None
        self.rescale_corp = None
        self.rescale_noncorp = None

    def calc_all_already_called(self):
        """
        Returns True if any response result is not None;
        otherwise returns False
        """
        return (self.investment_response is not None or
                self.debt_response is not None or
                self.rescale_corp is not None or
                self.rescale_noncorp is not None)

    def update_elasticities(self, new_elasticity_values):
        """
        Updates elasticities using info in new_elasticity_values dictionary
        """
        assert isinstance(new_elasticity_values, dict)
        # update elasiticity values
        for key in new_elasticity_values:
            if key not in self.elasticities:
                msg = '{} is not a valid elasticity name'
                raise ValueError(msg.format(key))
            self.elasticities[key] = new_elasticity_values[key]
        # test that elasticity values are valid
        assert self.elasticities['inv_usercost_c'] <= 0.0
        assert self.elasticities['inv_usercost_nc'] <= 0.0
        assert self.elasticities['inv_eatr_c'] <= 0.0
        assert self.elasticities['inv_eatr_nc'] <= 0.0
        assert self.elasticities['mne_share_c'] >= 0.0
        assert self.elasticities['mne_share_c'] <= 1.0
        assert self.elasticities['mne_share_nc'] >= 0.0
        assert self.elasticities['mne_share_nc'] <= 1.0
        assert self.elasticities['debt_taxshield_c'] >= 0.0
        assert self.elasticities['debt_taxshield_nc'] >= 0.0
        assert self.elasticities['reprate_inc'] <= 0.0
        assert self.elasticities['legalform_ratediff'] <= 0.0
        assert (self.elasticities['first_year_response']
                in range(START_YEAR, END_YEAR + 1))

    def calc_all(self, btax_params_base, btax_params_ref):
        """
        Executes all response calculations
        """
        self._calc_investment_response(btax_params_base, btax_params_ref)
        self._calc_debt_responses(btax_params_base, btax_params_ref)
        self._calc_repatriation_response(btax_params_base, btax_params_ref)
        self._calc_legal_response(btax_params_base, btax_params_ref)

    # ----- begin private methods of Release class -----

    def _calc_investment_response(self, btax_params_base, btax_params_ref):
        """
        Calculates percent change in investment & marginal product of capital,
        for each asset type, for each year, corporate and noncorporate.
        firstyear: when the firm behavioral response takes effect
        """
        # Read in the underlying functions for the investment response
        maindata = copy.deepcopy(Data().taxdep_info_gross('pre2017'))
        maindata.drop(['L_gds', 'L_ads', 'Method'], axis=1, inplace=True)
        # Extract relevant response parameters
        firstyear = self.elasticities['first_year_response']
        elast_c = self.elasticities['inv_usercost_c']
        elast_nc = self.elasticities['inv_usercost_nc']
        selast_c = self.elasticities['inv_eatr_c']
        selast_nc = self.elasticities['inv_eatr_nc']
        mne_share_c = self.elasticities['mne_share_c']
        mne_share_nc = self.elasticities['mne_share_nc']
        # No responses for years before first_year_response
        for year in range(START_YEAR, firstyear):
            ystr = str(year)
            maindata['deltaIc' + ystr] = 0.
            maindata['deltaInc' + ystr] = 0.
            maindata['MPKc' + ystr] = 0.
            maindata['MPKnc' + ystr] = 0.
        # Calculate cost of capital and EATR for every year for baseline
        btaxmini_base = BtaxMini(btax_params_base)
        years = range(firstyear, END_YEAR + 1)
        results_base = btaxmini_base.run_btax_mini(years)
        # Calculate cost of capital and EATR for every year for reform
        btaxmini_ref = BtaxMini(btax_params_ref)
        results_ref = btaxmini_ref.run_btax_mini(years)
        # Compare results to produce the responses
        for year in years:
            ystr = str(year)
            maindata['deltaIc' + ystr] = (((results_ref['u_c' + ystr]
                                            / results_base['u_c' + ystr] - 1)
                                           * elast_c +
                                           (results_ref['eatr_c' + ystr]
                                            - results_base['eatr_c' + ystr])
                                           * selast_c * mne_share_c))
            maindata['deltaInc' + ystr] = (((results_ref['u_nc' + ystr]
                                             / results_base['u_nc' + ystr] - 1)
                                            * elast_nc +
                                            (results_ref['eatr_nc' + ystr]
                                             - results_base['eatr_nc' + ystr])
                                            * selast_nc * mne_share_nc))
            maindata['MPKc' + ystr] = (results_ref['u_c' + ystr]
                                       + results_base['u_c' + ystr]) / 2.0
            maindata['MPKnc' + ystr] = (results_ref['u_nc' + ystr]
                                        + results_base['u_nc' + ystr]) / 2.0
        # Save the responses
        self.investment_response = copy.deepcopy(maindata)

    def _calc_debt_response_corp(self, btax_params_base, btax_params_ref):
        """
        Calculates corporate debt response.
        """
        # Extract the information on haircuts
        years = np.array(range(START_YEAR, END_YEAR + 1))
        fracded_base = np.array(btax_params_base['fracded_c'])
        fracded_ref = np.array(btax_params_ref['fracded_c'])
        elast_debt_list = np.where(
            years >= self.elasticities['first_year_response'],
            self.elasticities['debt_taxshield_c'], 0.0
        )
        taxshield_base = btax_params_base['tau_c']* fracded_base
        taxshield_ref = np.asarray(btax_params_ref['tau_c']) * fracded_ref
        pctch_delta = elast_debt_list * (taxshield_ref / taxshield_base - 1.)
        return pctch_delta

    def _calc_debt_response_noncorp(self, btax_params_base, btax_params_ref):
        """
        Calculates noncorporate debt response
        """
        # Extract information on haircuts
        id_hc_years = np.array(btax_params_ref['newIntPaid_noncorp_hcyear'])
        id_hc_new = np.array(btax_params_ref['newIntPaid_noncorp_hc'])
        years = np.array(range(START_YEAR, END_YEAR + 1))
        hclist = np.where(id_hc_years >= years, id_hc_new, 0.0)
        elast_debt_list = np.where(
            years >= self.elasticities['first_year_response'],
            self.elasticities['debt_taxshield_nc'], 0.0
        )
        taxshield_base = btax_params_base['tau_nc']
        taxshield_ref = btax_params_ref['tau_nc'] * (1 - hclist)
        pctch_delta = (taxshield_ref / taxshield_base - 1) * elast_debt_list
        return pctch_delta

    def _calc_debt_responses(self, btax_params_base, btax_params_ref):
        """
        Calls the functions to calculate debt responses and saves them in
        a DataFrame.
        """
        debtresp_c = self._calc_debt_response_corp(btax_params_base,
                                                   btax_params_ref)
        debtresp_nc = self._calc_debt_response_noncorp(btax_params_base,
                                                       btax_params_ref)
        debtresp_df = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                    'pchDelta_corp': debtresp_c,
                                    'pchDelta_noncorp': debtresp_nc})
        self.debt_response = debtresp_df

    def _calc_repatriation_response(self, btax_params_base, btax_params_ref):
        """
        Calculates the new repatriation rate of current CFC after-tax profits.
        The parameter used is the semi-elasticity of repatriations
        with respect to the tax penalty from repatriating, although it is
        implemented in exponential form instead of as a change. The response is
        only used for repatriations from current profits, as repatriations
        from accumulated profits are too complicated to model explicity
        and not relevant following the 2017 tax act.
        Note that although the set-up for this may seem odd, it is designed to
        ensure that no policy change results in to repatriation response,
        regardless of the semielasticity used. The appropriate value for the
        semi-elasticity is -10.66536949, which is consistent with the
        repatriation rate as of 2014.
        """
        # Get foreign tax rate
        ftax = Data().cfc_data.loc[0, 'taxrt']
        # Get domestic tax rate
        dtax_base = np.asarray(btax_params_base['tau_c'])
        dtax_ref = np.asarray(btax_params_ref['tau_c'])
        # Get foreign dividend inclusion rate for CFCs
        divrt_base = np.asarray(btax_params_base['foreign_dividend_inclusion'])
        divrt_ref = np.asarray(btax_params_ref['foreign_dividend_inclusion'])
        penalty_base = np.maximum(dtax_base - ftax, 0.) * divrt_base
        penalty_ref = np.maximum(dtax_ref - ftax, 0.) * divrt_ref
        # Compute repatriation rates
        reprate_base = np.exp(-penalty_base * self.elasticities['reprate_inc'])
        reprate_ref = np.exp(-penalty_ref * self.elasticities['reprate_inc'])
        # Compute change in repatriation rate
        reprate_ch = np.zeros(14)
        for i in range(14):
            if i + 2014 >= self.elasticities['first_year_response']:
                reprate_ch[i] = reprate_ref[i] - reprate_base[i]
        repat_response = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                       'reprate_e': reprate_ch,
                                       'reprate_a': np.zeros(14)})
        self.repatriation_response = repat_response

    def _calc_legal_response(self, btax_params_base, btax_params_ref):
        """
        Reallocation of business activity between corporate and noncorporate
        sections, achieved by modifying the rescaling factors. For now,
        assuming identical tax bases.
        """
        self.rescale_corp = np.ones(NUM_YEARS)
        self.rescale_noncorp = np.ones(NUM_YEARS)
        """
        elast = self.elasticities['legalform_ratediff']
        firstyear = self.elasticities['first_year_response']
        elast_list = np.zeros(NUM_YEARS)
        for i in range(NUM_YEARS):
            if i + START_YEAR >= firstyear:
                elast_list[i] = elast
        tau_nc_base = btax_params_base['tau_nc']
        tau_c_base = btax_params_base['tau_c']
        tau_nc_ref = btax_params_ref['tau_nc']
        tau_c_ref = btax_params_ref['tau_c']
        tau_e_base = btax_params_base['tau_e']
        tau_e_ref = btax_params_ref['tau_e']
        taxterm_base = (tau_c_base + tau_e_base - tau_c_base * tau_e_base -
                        tau_nc_base)
        taxterm_ref = (tau_c_ref + tau_e_ref - tau_c_ref * tau_e_ref
                       - tau_nc_ref)
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
