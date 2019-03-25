"""
Business-Taxation Investor class.
"""
import copy
import numpy as np
import pandas as pd
import taxcalc as itax
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data


class Investor():
    """
    Constructor for the Investor class.

    This class provides information on effective marginal tax rates on
    investment income and distributes changes in corporate after-tax income
    and pass-through business net income.

    Parameters:
        refdict: individual-income-tax reform dict for itax.Policy class
        data: investor data for itax.Records class
    """

    def __init__(self, refdict=None, data='puf.csv'):
        # Specify refdict
        if refdict is None:
            self.refdict = {}
        if isinstance(refdict, dict):
            self.refdict = refdict
        else:
            raise ValueError('refdict must be a dictionary or None')
        # Specify records_data
        if isinstance(data, str) or isinstance(data, pd.DataFrame):
            self.records_data = data
        else:
            raise ValueError('data must be a string or a Pandas DataFrame')
        # MTRs needed for calculating tax rates on business equity
        self.needed_mtr_list = ['e00900p', 'e26270', 'e02000', 'e01700',
                                'e00650', 'p22250', 'p23250']

    def initiate_calculator(self):
        """
        Creates an intial version of the itax.Calculator object for START_YEAR
        """
        policy = itax.Policy()
        records = itax.Records(data=self.records_data)
        if self.refdict != {}:
            policy.implement_reform(self.refdict)
        calc = itax.Calculator(policy=policy, records=records, verbose=False)
        calc.advance_to_year(START_YEAR)
        calc.calc_all()
        return calc

    def calc_tauNC(self, mtrdict, incdict):
        """
        Calculate the effective marginal tax rate on noncorporate business income.
        """
        # Shares of noncorporate equity in fully taxable and tax-deferred form.
        alpha_nc_ft = 0.763
        alpha_nc_td = 0.101
        mtr1 = mtrdict['e00900p']
        mtr2 = mtrdict['e26270']
        mtr3 = mtrdict['e02000']
        mtr4 = mtrdict['e01700']
        posti = (incdict['taxinc'] > 0.)
        inc1 = np.abs(incdict['SchC'])
        inc2 = np.abs(incdict['SchEactive'])
        inc3 = np.abs(incdict['SchEpassive'])
        inc4 = incdict['definc']
        wgt = incdict['wgt']
        mtr_ft = (sum((mtr1 * inc1 + mtr2 * inc2 + mtr3 * inc3) * posti * wgt) /
                  sum((inc1 + inc2 + inc3) * posti * wgt))
        mtr_td = sum(mtr4 * inc4 * posti * wgt) / sum(inc4 * posti * wgt)
        mtr_nc = alpha_nc_ft * mtr_ft + alpha_nc_td * mtr_td
        return mtr_nc

    def calc_tauE(self, mtrdict, incdict, year):
        """
        Calculate the effective marginal tax rate on equity income in year.
        """
        # Retained earnings rate
        m = 0.44
        # Nominal expected return to equity
        iyr = year - START_YEAR
        E = (Data().econ_defaults['r_e_c'][iyr]
             + Data().econ_defaults['pi'][iyr])
        # shares of cg in short-term, long-term, and held until death
        omega_scg = 0.034
        omega_lcg = 0.496
        omega_xcg = 1 - omega_scg - omega_lcg
        # shares of corp equity in taxable, deferred and nontaxable form
        alpha_ft = 0.572
        alpha_td = 0.039
        alpha_nt = 0.389
        # holding period for equity
        h_scg = 0.5
        h_lcg = 8.0
        h_td = 8.0
        # Get MTRs
        mtr_d = mtrdict['e00650']
        mtr_scg = mtrdict['p22250']
        mtr_lcg = mtrdict['p23250']
        mtr_td = mtrdict['e01700']
        # Get income measures
        inc_d = incdict['div']
        inc_scg = np.where(incdict['stcg'] >= 0, incdict['stcg'], 0)
        inc_lcg = np.where(incdict['ltcg'] >= 0, incdict['ltcg'], 0)
        inc_td = incdict['definc']
        posti = (incdict['taxinc'] > 0.)
        wgt = incdict['wgt']
        # MTR on dividend income
        tau_d = sum(mtr_d * inc_d * posti * wgt) / sum(inc_d * posti * wgt)
        # accrual effective mtr on stcg
        tau_scg1 = (sum(mtr_scg * inc_scg * posti * wgt) /
                    sum(inc_scg * posti * wgt))
        tau_scg = 1 - (np.log(np.exp(m * E * h_scg) * (1 - tau_scg1) + tau_scg1) /
                       (m * E * h_scg))
        # accrual effective mtr on ltcg
        tau_lcg1 = (sum(mtr_lcg * inc_lcg * posti * wgt) /
                    sum(inc_lcg * posti * wgt))
        tau_lcg = 1 - (np.log(np.exp(m * E * h_lcg)
                              * (1 - tau_lcg1) + tau_lcg1) / (m * E * h_lcg))
        # mtr on capital gains held until death
        tau_xcg = 0.0
        tau_cg = (omega_scg * tau_scg
                  + omega_lcg * tau_lcg
                  + omega_xcg * tau_xcg)
        tau_ft = (1 - m) * tau_d + m * tau_cg
        tau_td1 = (sum(mtr_td * inc_td * posti * wgt)
                   / sum(inc_td * posti * wgt))
        tau_td = 1 - (np.log(np.exp(E * h_td) * (1 - tau_td1) + tau_td1) /
                      (E * h_td))
        tau_e = alpha_ft * tau_ft + alpha_td * tau_td + alpha_nt * 0.0
        return tau_e

    def gen_mtr_lists(self):
        # Calculate the EMTR on income from corporate equity
        # and non-corporate business.
        mtrlist_nc = np.zeros(NUM_YEARS)
        mtrlist_e = np.zeros(NUM_YEARS)
        calc1 = self.initiate_calculator()
        for year in range(START_YEAR, END_YEAR + 1):
            calc1.advance_to_year(year)
            calc1.calc_all()
            # Get individual MTRs on each income type
            mtr1 = dict()
            for var in self.needed_mtr_list:
                _, _, mtr1[var] = calc1.mtr(var, calc_all_already_called=True)
            # Get relevant income measures
            inc1 = dict()
            inc1['SchC'] = calc1.array('e00900')
            inc1['SchEactive'] = calc1.array('e26270')
            inc1['SchEpassive'] = calc1.array('e02000') - calc1.array('e26270')
            inc1['definc'] = calc1.array('e01700')
            inc1['div'] = calc1.array('e00650')
            inc1['stcg'] = calc1.array('p22250')
            inc1['ltcg'] = calc1.array('p23250')
            inc1['wgt'] = calc1.array('s006')
            inc1['taxinc'] = calc1.array('c04800')
            # Calculate and save overall MTRs
            iyr = year - START_YEAR
            mtrlist_nc[iyr] = self.calc_tauNC(mtr1, inc1)
            mtrlist_e[iyr] = self.calc_tauE(mtr1, inc1, year)
        self.mtrlist_nc = mtrlist_nc
        self.mtrlist_e = mtrlist_e

    def get_tauNClist(self):
        """
        Returns mtrlist_nc as an array
        """
        return np.array(self.mtrlist_nc)

    def get_tauElist(self):
        """
        Returns mtrlist_e as an array
        """
        return np.array(self.mtrlist_e)

    def distribute_results(self, multipliers):
        """
        Pass effects of business tax reform to itax.
        Adjusts individual income based on growth factors.
        Adjusts noncorporate business credits based on rescaling factors from
        legal shifting response.
        """
        calc1 = self.initiate_calculator()
        indiv_revenue = np.zeros(NUM_YEARS)
        for iyr in range(0, NUM_YEARS):
            year = iyr + START_YEAR
            calc2 = copy.deepcopy(calc1)
            # Change Sch C business income
            ref2_e00900p = calc2.array('e00900p')
            ref2_e00900s = calc2.array('e00900s')
            ref2_e00900 = calc2.array('e00900')
            ref3_e00900p = np.where(ref2_e00900p >= 0,
                                    ref2_e00900p * multipliers['SchC_pos'][iyr],
                                    ref2_e00900p * multipliers['SchC_neg'][iyr])
            ref3_e00900s = np.where(ref2_e00900s >= 0,
                                    ref2_e00900s * multipliers['SchC_pos'][iyr],
                                    ref2_e00900s * multipliers['SchC_neg'][iyr])
            ref3_e00900 = np.where(ref2_e00900 >= 0,
                                   ref2_e00900 * multipliers['SchC_pos'][iyr],
                                   ref2_e00900 * multipliers['SchC_neg'][iyr])
            calc2.array('e00900p', ref3_e00900p)
            calc2.array('e00900s', ref3_e00900s)
            calc2.array('e00900', ref3_e00900)
            # Change Sch E business income
            ref2_e26270 = calc2.array('e26270')
            change_e26270 = np.where(ref2_e26270 >= 0,
                                     ref2_e26270 * (multipliers['e26270_pos'][iyr] - 1),
                                     ref2_e26270 * (multipliers['e26270_neg'][iyr] - 1))
            ref3_e26270 = ref2_e26270 + change_e26270
            ref3_e02000 = calc2.array('e02000') + change_e26270
            calc2.array('e26270', ref3_e26270)
            calc2.array('e02000', ref3_e02000)
            # Change investment income
            calc2.array('e00600', calc2.array('e00600') * multipliers['equity'][iyr])
            calc2.array('e00650', calc2.array('e00650') * multipliers['equity'][iyr])
            calc2.array('p22250', calc2.array('p22250') * multipliers['equity'][iyr])
            calc2.array('p23250', calc2.array('p23250') * multipliers['equity'][iyr])
            # Change noncorporate business credits
            calc2.array('e07300', calc2.array('e07300') * multipliers['rescale_noncorp'][iyr])
            calc2.array('e07400', calc2.array('e07400') * multipliers['rescale_noncorp'][iyr])
            calc2.array('e07600', calc2.array('e07600') * multipliers['rescale_noncorp'][iyr])
            calc2.calc_all()
            # Calculate total individual income and payroll tax revenue
            indiv_revenue[iyr] = calc2.weighted_total('combined') * 1e-9
            # Advance calc1 to the next year and recalculate
            if year < END_YEAR:
                calc1.increment_year()
                calc1.calc_all()
        self.revenue_postdistribution = indiv_revenue

    def undistributed_revenue(self):
        """
        Calculates individual income tax revenue for each year without
        distributing any tax changes.
        """
        calc1 = self.initiate_calculator()
        indiv_revenue = np.zeros(NUM_YEARS)
        for iyr in range(0, NUM_YEARS):
            year = iyr + START_YEAR
            indiv_revenue[iyr] = calc1.weighted_total('combined') * 1e-9
            if year < END_YEAR:
                calc1.increment_year()
                calc1.calc_all()
        self.revenue_predistribution = indiv_revenue

    def get_revenue_withdistribution(self):
        """
        Returns total individual income tax revenue after corporate tax
        distribution and noncorporate business income distribution.
        """
        return np.array(self.revenue_postdistribution)

    def get_revenue_nodistribution(self):
        """
        Returns total individual income tax revenue with no business income
        distribution.
        """
        return np.array(self.revenue_predistribution)
