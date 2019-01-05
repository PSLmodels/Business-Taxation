import numpy as np
import pandas as pd
import copy
from data import Data
from corporation import Corporation
from passthrough import PassThrough
from investor import Investor
from response import Response


class BusinessModel():
    """
    Constructor for the BusinessModel class. This class must include 
    baseline objects and reform objects, in order to correctly estimate the 
    effects of changing policy parameters.
    For each policy set (baseline and reform), the following objects are
    created:
        Corporation
        PassThrough
        Investor
    Furthermore, the BusinessModel may also create a Response object. 
    It is important to note that the inclusion of both a baseline and a reform
    scenario is important: the necessity of both comes into play when
    calculating the Response and when distributing the changes in corporate
    income and business income to tax units. 
    
    Parameters:
        btax_refdict: main business policy reform dictionary
        other_refdict: special business policy reform dictionary
        iit_refdict: individual policy reform dictionary (for taxcalc)
        btax_basedict: business policy baseline dictionary (default none)
        other_basedict: special policy baseline dictionary (default none)
        iit_basedict: individual policy baseline dictionary (default none)
        elast_dict: dictionary of elasticities for firm responses
    """
    
    def __init__(self, btax_refdict, other_refdict, iit_refdict,
                 btax_basedict={}, other_basedict={}, iit_basedict={},
                 elast_dict=None):
        # Set default policy parameters for later use
        self.btax_defaults = Data().btax_defaults
        self.brc_defaults_other = Data().brc_defaults_other
        # Create the baseline and reform parameter storing forms
        self.btax_params_base = self.update_btax_params(btax_basedict)
        self.btax_params_ref = self.update_btax_params(btax_refdict)
        self.other_params_base = self.update_brc_params(other_basedict)
        self.other_params_ref = self.update_brc_params(other_refdict)
        # Create Investors
        self.investor_base = Investor(iit_basedict)
        self.investor_ref = Investor(iit_refdict)
        # Create Corporations
        self.corp_base = Corporation(self.btax_params_base, self.other_params_base)
        self.corp_ref = Corporation(self.btax_params_ref, self.other_params_ref)
        # Create PassThroughs
        self.passthru_base = PassThrough(self.btax_params_base, self.other_params_base)
        self.passthru_ref = PassThrough(self.btax_params_ref, self.other_params_ref)
        # Save the elasticity dictionary
        if elast_dict is not None:
            self.check_elast_dict(elast_dict)
            self.elast_dict = elast_dict
        else:
            self.elast_dict = Data().elast_defaults
    
    def check_btax_reform(self, paramdict):
        """
        Checks that the btax_param dictionary are acceptable
        """
        assert isinstance(paramdict, dict)
        paramnames = list(self.btax_defaults)
        paramnames.remove('year')
        for key in paramdict:
            key2 = int(key)
            assert key2 in range(2014, 2027)
            for param in paramdict[key]:
                assert param in paramnames
    
    def check_other_reform(self, paramdict):
        """
        Checks that the other parameter dictionaries are acceptable
        """
        assert isinstance(paramdict, dict)
        for key in paramdict:
            assert key in self.brc_defaults_other.keys()
        if 'reclassify_taxdep_gdslife' in paramdict:
            year = list(paramdict['reclassify_taxdep_gdslife'].keys())[0]
            for life in paramdict['reclassify_taxdep_gdslife'][year]:
                assert life in [3, 5, 7, 10, 15, 20, 25, 27.5, 39]
        if 'reclassify_taxdep_adslife' in paramdict:
            year = list(paramdict['reclassify_taxdep_adslife'].keys())[0]
            for life in paramdict['reclassify_taxdep_adslife'][year]:
                assert life in [3, 4, 5, 6, 7, 9, 9.5, 10, 12, 14, 15,
                                18, 19, 20, 25, 28, 30, 40, 50, 100]
    
    def update_btax_params(self, param_dict):
        """
        Updates btax_params
        param_dict is a year: {param: value} dictionary.
        Acceptable years are 2017-2027. Ex:
            {'2018': {'tau_c': 0.3}}
        """
        self.check_btax_reform(param_dict)
        params_df = copy.deepcopy(self.btax_defaults)
        yearlist = []
        for key in param_dict:
            yearlist.append(key)
        yearlist.sort()
        years = np.asarray(params_df['year'])
        for year in yearlist:
            for param in param_dict[year]:
                paramlist1 = np.asarray(params_df[param])
                paramlist1[years >= int(year)] = param_dict[year][param]
                params_df[param] = paramlist1
        return params_df    
    
    def update_brc_params(self, paramdict_other):
        """
        Updates other_params
        """
        self.check_other_reform(paramdict_other)
        other_params = copy.deepcopy(self.brc_defaults_other)
        for key in paramdict_other:
            other_params[key] = paramdict_other[key]
        return other_params
    
    def produce_multipliers(self):
        # Get corporate net after-tax incomes
        netinc_corp_base = self.corp_base.get_netinc()
        netinc_corp_ref = self.corp_ref.get_netinc()
        # Calculate multiplier for equity income
        equity_multiplier = netinc_corp_ref / netinc_corp_base
        # Save into DataFrame
        multipliers = pd.DataFrame({'year': range(2014, 2028),
                                    'equity': equity_multiplier})
        # Get net income results for the pass-throughs
        netinc_ptbase = copy.deepcopy(self.passthru_base.netinc_results)
        netinc_ptref = copy.deepcopy(self.passthru_ref.netinc_results)
        multipliers['SchC_pos'] = netinc_ptref['SchC_pos'] / netinc_ptbase['SchC_pos']
        multipliers['SchC_neg'] = netinc_ptref['SchC_neg'] / netinc_ptbase['SchC_neg']
        multipliers['e26270_pos'] = (netinc_ptref['partner_pos'] + netinc_ptref['Scorp_pos']) / (netinc_ptbase['partner_pos'] + netinc_ptbase['Scorp_pos'])
        multipliers['e26270_neg'] = (netinc_ptref['partner_neg'] + netinc_ptref['Scorp_neg']) / (netinc_ptbase['partner_neg'] + netinc_ptbase['Scorp_neg'])
        # Corporate interest share of all interest
        # Note: interest income not distributed to debtholders (yet)
        corpshare_totalint = 1.0
        multipliers['debt'] = (1 + (self.corp_ref.real_results['NIP'] / self.corp_base.real_results['NIP'] - 1) * corpshare_totalint)
        # Add recale results
        multipliers['rescale_corp'] = self.corp_ref.data.rescale_corp / self.corp_base.data.rescale_corp
        multipliers['rescale_noncorp'] = self.corp_ref.data.rescale_noncorp / self.corp_base.data.rescale_noncorp
        # Save multipliers
        self.multipliers = multipliers
    
    def calc_revenue_changes(self):
        """
        Calculates the change in corporate tax revenue, the change in 
        individual income tax/payroll tax revenue, and the combination. Saves 
        these changes in a DataFrame.
        """
        corprev_base = self.corp_base.get_taxrev()
        corprev_ref = self.corp_ref.get_taxrev()
        corprev_change = corprev_ref - corprev_base
        indivrev_base = self.investor_base.get_revenue_nodistribution()
        indivrev_ref = self.investor_ref.get_revenue_withdistribution()
        indivrev_change = indivrev_ref - indivrev_base
        alltax_change = corprev_change + indivrev_change
        self.ModelResults = pd.DataFrame({'year': range(2014,2028),
                                          'CTax_change': corprev_change,
                                          'ITax_change': indivrev_change,
                                          'AllTax_change': alltax_change})
        
    def calc_noresponse(self):
        """
        Executes all calculations, with no Response
        """
        # Run static calculations for corporations
        self.corp_base.calc_static()
        self.corp_ref.calc_static()
        # Run static calculations for pass-throughs
        self.passthru_base.calc_static()
        self.passthru_ref.calc_static()
        # Compare corporations and pass-throughs to get income changes
        self.produce_multipliers()
        # Distribute changes to reform investor
        self.investor_ref.distribute_results(self.multipliers)
        # Calculate baseline investor without distributing
        self.investor_base.undistributed_revenue()
        # Calculate and save total revenue changes
        self.calc_revenue_changes()
    
    def check_elast_dict(self, elast_params):
        """
        Checks the elasticities for the responses to ensure that it includes
        all relevant elasticities and that these have reasonable values.
        """            
        # check that all necessary terms included or defined
        for key in ['inv_usercost_c', 'inv_usercost_nc', 'inv_eatr_c',
                    'inv_eatr_nc', 'mne_share_c', 'mne_share_nc',
                    'debt_taxshield_c', 'debt_taxshield_nc',
                    'legalform_ratediff', 'first_year_response']:
            assert key in elast_params
        # test that values are correct
        assert elast_params['inv_usercost_c'] <= 0.0
        assert elast_params['inv_usercost_nc'] <= 0.0
        assert elast_params['inv_eatr_c'] <= 0.0
        assert elast_params['inv_eatr_nc'] <= 0.0
        assert elast_params['mne_share_c'] >= 0.0
        assert elast_params['mne_share_c'] <= 1.0
        assert elast_params['mne_share_nc'] >= 0.0
        assert elast_params['mne_share_nc'] <= 1.0
        assert elast_params['debt_taxshield_c'] >= 0.0
        assert elast_params['debt_taxshield_nc'] >= 0.0
        assert elast_params['legalform_ratediff'] <= 0.0
        assert elast_params['first_year_response'] in range(2014, 2028)
    
    def update_elasticities(self, dict2):
        """
        Updates the elast_dict object
        """
        elast_dict2 = copy.deepcopy(self.elast_dict)
        for key in dict2:
            elast_dict2[key] = dict2[key]
        self.check_elast_dict(elast_dict2)
        self.elast_dict = elast_dict2
    
    def update_mtrlists(self):
        """
        Calls Investors to calculate MTRs on noncorporate business equity
        and on corporate equity, and updates these in the Response object.
        """
        # Generate MTRs for baseline investor
        self.investor_base.gen_mtr_lists()
        self.btax_params_base['tau_nc'] = self.investor_base.get_tauNClist()
        self.btax_params_base['tau_e'] = self.investor_base.get_tauElist()
        # Generate MTRs for reform investor
        self.investor_ref.gen_mtr_lists()
        self.btax_params_ref['tau_nc'] = self.investor_ref.get_tauNClist()
        self.btax_params_ref['tau_e'] = self.investor_ref.get_tauElist()
    
    def calc_withresponse(self):
        # Calculate MTRs and update all policy DataFrames (btax_params)
        self.update_mtrlists()
        # Create Response object and execute all responses
        self.response = Response(self.elast_dict, self.btax_params_base, self.btax_params_ref, self.other_params_base, self.other_params_ref)
        self.response.calc_all()
        # Run calculations for corporations
        self.corp_base.calc_static()
        self.corp_ref.apply_responses(self.response)
        # Run calculations for pass-throughs
        self.passthru_base.calc_static()
        self.passthru_ref.apply_responses(self.response)
        # Compare corporations and pass-throughs to get income changes
        self.produce_multipliers()
        # Distribute changes to reform investor
        self.investor_ref.distribute_results(self.multipliers)
        # Calculate baseline investor without distributing
        self.investor_base.undistributed_revenue()
        # Calculate and save total revenue changes
        self.calc_revenue_changes()
    
    
    