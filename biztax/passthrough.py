import numpy as np
import pandas as pd
import copy
from biztax.data import Data
from biztax.asset import Asset
from biztax.debt import Debt
from biztax.response import Response


class PassThrough():
    """
    Constructor for the PassThrough class.
    
    This contains the calculation of pass-through business income. All other
    components of pass-through taxation occur through Tax-Calculator.
    
    For now, a PassThrough object contains 6 different business entities:
        sole proprietorship, positive net income
        sole proprietorship, negative net income
        S corporation, positive net income
        S corporation, negative net income
        partnership, positive net income
        partnership, negative net income
    Therefore, the process for modeling the pass-through sector evolves in 
    two stages. The first, like for the Corporation class, produces a single
    Asset object, Debt object and earnings for the pass-through sector. Once
    these are calculated, they are split between each of the 6 entities. The
    results from these will later be used by the Investor class to distribute
    the changes in business income to individuals in Tax-Calculator. 
    
    The following functions apply to the sector as a whole:
        create_asset()
        create_earnings()
        create_debt()
       real_activity() 
    """
    
    def __init__(self, btax_params):
        # Store policy parameter objects
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        # Create Data object
        self.data = Data()
        # Create Asset object and calculate
        self.asset = Asset(self.btax_params, corp=False, data=self.data)
        self.asset.calc_all()
    
    def create_earnings(self):
        """
        Creates the initial forecast for earnings. Static only.
        """
        # Get initial EBITDA for 2014, for those in net income positions
        sp_posinc2014 = np.array(self.data.sp_data['netinc'])[-1]
        part_posinc2014 = np.array(self.data.partner_data['netinc_total'])[-1]
        scorp_posinc2014 = np.array(self.data.Scorp_data['netinc_total'])[-1]
        # Get initial EBITDA for 2014, for those in net loss positions
        sp_neginc2014 = -np.array(self.data.sp_data['netloss'])[-1]
        part_neginc2014 = -np.array(self.data.partner_data['netloss_total'])[-1]
        scorp_neginc2014 = -np.array(self.data.Scorp_data['netloss_total'])[-1]
        # Get growth factor for noncorporate business income and apply it
        gfact_propinc = np.array(self.data.gfactors['propinc_nonfarm'])[1:]
        sp_posinc = sp_posinc2014 / gfact_propinc[0] * gfact_propinc
        part_posinc = part_posinc2014 / gfact_propinc[0] * gfact_propinc
        scorp_posinc = scorp_posinc2014 / gfact_propinc[0] * gfact_propinc
        sp_neginc = sp_neginc2014 / gfact_propinc[0] * gfact_propinc
        part_neginc = part_neginc2014 / gfact_propinc[0] * gfact_propinc
        scorp_neginc = scorp_neginc2014 / gfact_propinc[0] * gfact_propinc
        # Aggregate and save EBITDAs
        total_inc = (sp_posinc + sp_neginc + part_posinc + part_neginc +
                     scorp_posinc + scorp_neginc)
        earnings_result = pd.DataFrame({'year': range(2014,2028),
                                        'total': total_inc,
                                        'SchC_pos': sp_posinc,
                                        'SchC_neg': sp_neginc,
                                        'partner_pos': part_posinc,
                                        'partner_neg': part_neginc,
                                        'Scorp_pos': scorp_posinc, 
                                        'Scorp_neg': scorp_neginc})
        self.earnings = earnings_result
    
    def create_debt(self):
        """
        Creates the Debt object for the pass-through sector. 
        Note: create_asset must have already been called
        """
        self.debt = Debt(self.btax_params, self.asset.get_forecast(),
                         data=self.data, corp=False)
        self.debt.calc_all()
    
    def real_activity(self):
        """
        Produces a DataFrame of the pass-through sector's real activity.
        Real measures are:
            Capital stock
            Investment
            Depreciation (economic)
            Debt
            Interest paid
            Earnings
            Net income
            Cash flow
        Note that unlike for a corporation, the final real activity measures
        (net income and cash flow) are pre-tax, as these would be passed to
        units in Tax-Calculator. 
        """
        real_results = pd.DataFrame({'year': range(2014,2028),
                                     'Earnings': self.earnings['total']})
        real_results['Kstock'] = self.asset.get_forecast()
        real_results['Inv'] = self.asset.get_investment()
        real_results['Depr'] = self.asset.get_truedep()
        real_results['Debt'] = self.debt.get_debt()
        real_results['NIP'] = self.debt.get_nip()
        real_results['NetInc'] = real_results['Earnings'] - real_results['Depr'] - real_results['NIP']
        real_results['CashFlow'] = real_results['Earnings'] - real_results['Inv']
        self.real_results = real_results
    
    def calc_schC(self):
        """
        Calculates net income for sole proprietorships
        """
        SchC_results = pd.DataFrame({'year': range(2014,2028)})
        # Update earnings
        SchC_results['ebitda_pos'] = self.earnings['SchC_pos']
        SchC_results['ebitda_neg'] = self.earnings['SchC_neg']
        # Update tax depreciation
        SchC_results['dep_pos'] = (self.asset.get_taxdep() * self.data.depshare_sp_posinc)
        SchC_results['dep_neg'] = (self.asset.get_taxdep() * self.data.depshare_sp_neginc)
        # Update interest deduction
        SchC_results['intded_pos'] = (self.debt.get_nid() * self.data.intshare_sp_posinc)
        SchC_results['intded_neg'] = (self.debt.get_nid() * self.data.intshare_sp_neginc)
        # Update business net income
        SchC_results['netinc_pos'] = SchC_results['ebitda_pos'] - SchC_results['dep_pos'] - SchC_results['intded_pos']
        SchC_results['netinc_neg'] = SchC_results['ebitda_neg'] - SchC_results['dep_neg'] - SchC_results['intded_neg']
        self.SchC_results = SchC_results
    
    def calc_partner(self):
        """
        Calculates net income for partnerships
        """
        partner_results = pd.DataFrame({'year': range(2014,2028)})
        # Update earnings
        partner_results['ebitda_pos'] = self.earnings['partner_pos']
        partner_results['ebitda_neg'] = self.earnings['partner_neg']
        # Update tax depreciation
        partner_results['dep_pos'] = (self.asset.get_taxdep() * self.data.depshare_partner_posinc)
        partner_results['dep_neg'] = (self.asset.get_taxdep() * self.data.depshare_partner_neginc)
        # Update interest deduction
        partner_results['intded_pos'] = (self.debt.get_nid() * self.data.intshare_partner_posinc)
        partner_results['intded_neg'] = (self.debt.get_nid() * self.data.intshare_partner_neginc)
        # Update business net income
        partner_results['netinc_pos'] = partner_results['ebitda_pos'] - partner_results['dep_pos'] - partner_results['intded_pos']
        partner_results['netinc_neg'] = partner_results['ebitda_neg'] - partner_results['dep_neg'] - partner_results['intded_neg']
        self.partner_results = partner_results
    
    def calc_Scorp(self):
        """
        Calculates net income for S corporations
        """
        Scorp_results = pd.DataFrame({'year': range(2014,2028)})
        # Update earnings
        Scorp_results['ebitda_pos'] = self.earnings['Scorp_pos']
        Scorp_results['ebitda_neg'] = self.earnings['Scorp_neg']
        # Update tax depreciation
        Scorp_results['dep_pos'] = (self.asset.get_taxdep() * self.data.depshare_scorp_posinc)
        Scorp_results['dep_neg'] = (self.asset.get_taxdep() * self.data.depshare_scorp_neginc)
        # Update interest deduction
        Scorp_results['intded_pos'] = (self.debt.get_nid() * self.data.intshare_scorp_posinc)
        Scorp_results['intded_neg'] = (self.debt.get_nid() * self.data.intshare_scorp_neginc)
        # Update business net income
        Scorp_results['netinc_pos'] = Scorp_results['ebitda_pos'] - Scorp_results['dep_pos'] - Scorp_results['intded_pos']
        Scorp_results['netinc_neg'] = Scorp_results['ebitda_neg'] - Scorp_results['dep_neg'] - Scorp_results['intded_neg']
        self.Scorp_results = Scorp_results
    
    def calc_netinc(self):
        """
        Runs all calculations for each entity and saves the net income results.
        """
        self.calc_schC()
        self.calc_partner()
        self.calc_Scorp()
        netinc_results = pd.DataFrame({'year': range(2014,2028)})
        netinc_results['SchC_pos'] = self.SchC_results['netinc_pos']
        netinc_results['SchC_neg'] = self.SchC_results['netinc_neg']
        netinc_results['partner_pos'] = self.SchC_results['netinc_pos']
        netinc_results['partner_neg'] = self.SchC_results['netinc_neg']
        netinc_results['Scorp_pos'] = self.SchC_results['netinc_pos']
        netinc_results['Scorp_neg'] = self.SchC_results['netinc_neg']
        self.netinc_results = netinc_results
    
    def calc_static(self):
        """
        Runs the static calculations
        """
        self.create_earnings()
        self.create_debt()
        self.real_activity()
        self.calc_netinc()
    
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
            mpk = np.array(responses.investment_response['MPKnc' + str(j + 2014)])
            for i in range(96): # by asset
                changeEarnings[i,j] = deltaK[i,j] * mpk[i] * self.data.adjfactor_dep_noncorp
        deltaE = np.zeros(14)
        for j in range(14):
            deltaE[j] = changeEarnings[:, j].sum()
        earnings_old = np.array(self.earnings['total'])
        ebitda_chgfactor = (earnings_old + deltaE) * self.data.rescale_noncorp / earnings_old
        keylist = list(self.earnings)
        for key in keylist:
            self.earnings[key] = self.earnings[key] * ebitda_chgfactor
    
    def update_debt(self, responses):
        """
        Replaces the Debt object to use the new asset forecast and Data
        """
        pctch_delta = np.array(responses.debt_response['pchDelta_corp'])
        self.debt = Debt(self.btax_params, self.asset.get_forecast(),
                         data=self.data, response=pctch_delta, corp=False)
        self.debt.calc_all()
    
    def apply_responses(self, responses):
        """
        Updates Data, Asset, earnings, and Debt to include 
        responses.
        """
        assert isinstance(responses, Response)
        self.update_legal(responses)
        self.update_investment(responses)
        self.update_earnings(responses)
        self.update_debt(responses)
        self.real_activity()
        self.calc_netinc()
    
    
