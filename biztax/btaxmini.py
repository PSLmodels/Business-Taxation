"""
Business-Taxation BtaxMini class.
"""
import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.asset import Asset


class BtaxMini():
    """
    Constructor for the BtaxMini class. This class functions similarly to
    the B-Tax model, with several modifications, such as the use of different
    equations and allowing for nonconstant tax rates, as well as producing
    somewhat different final measures.

    Parameters
    ----------
    btax_params: DataFrame of regular tax parameters

    Returns
    -------
    DataFrame of user cost of capital and EATR for each year and asset type
    """

    def __init__(self, btax_params):
        self.econ_params = copy.deepcopy(Data().econ_defaults)
        self.btax_params = btax_params
        self.asset_c = Asset(btax_params, corp=True)
        self.asset_c.build_deprLaw_matrices()

    def make_tdict_c(self, start_year):
        """
        Produces a dictionary of tax rates and changes to those rates,
        for use when calculating rho and EATR, for corporations.
        Assumes no changes after END_YEAR.
        """
        assert start_year >= 2017
        assert type(start_year) == int
        if start_year >= END_YEAR:
            tdict = {'0': self.btax_params['tau_c'][10]}
        else:
            tdict = {'0': self.btax_params['tau_c'][start_year-START_YEAR]}
            for i in range(start_year - 2016, len(self.btax_params['year']) - 3):
                if self.btax_params['tau_c'][i+3] != self.btax_params['tau_c'][i+2]:
                    tdict[str(i - (start_year-2017))] = self.btax_params['tau_c'][i+3]
        return tdict

    def make_tdict_nc(self, start_year):
        """
        Produces a dictionary of tax rates and changes to those rates,
        for use when calculating rho and EATR, for noncorporate businesses.
        Assumes no changes after END_YEAR.
        """
        assert start_year >= 2017
        assert type(start_year) == int
        if start_year >= END_YEAR:
            tdict = {'0': self.btax_params['tau_nc'][13]}
        else:
            tdict = {'0': self.btax_params['tau_nc'][start_year-START_YEAR]}
            for i in range(start_year - 2016, len(self.btax_params['year']) - 3):
                tdict[str(i - (start_year-2017))] = self.btax_params['tau_nc'][i+3]
        return tdict

    def get_econ_params_oneyear(self, year):
        """
        Extracts the economic parameters to use for calculations in each year.
        """
        r_d = self.econ_params['r_d'][year-START_YEAR]
        r_e_c = self.econ_params['r_e_c'][year-START_YEAR]
        r_e_nc = self.econ_params['r_e_nc'][year-START_YEAR]
        pi = self.econ_params['pi'][year-START_YEAR]
        f_c = self.econ_params['f_c'][year-START_YEAR]
        f_nc = self.econ_params['f_nc'][year-START_YEAR]
        r_c = f_c * r_d + (1 - f_c) * r_e_c
        r_nc = f_nc * r_d + (1 - f_nc) * r_e_nc
        return(r_c, r_nc, r_d, pi, f_c, f_nc)

    def calc_frac_ded(self, year):
        """
        Calculates the fraction of interest deductible for the given year,
        for corporate and noncorporate.
        """
        iyr = year - START_YEAR
        # Extract the corporate interest haircuts
        hc_nid_c = np.array(self.btax_params['intPaid_corp_hc'])[iyr]
        hc_id_new_year_c = np.array(self.btax_params['newIntPaid_corp_hcyear'])[iyr]
        hc_id_new_c = np.array(self.btax_params['newIntPaid_corp_hc'])[iyr]
        # Find haircut for corporations
        fracdedc = 1.0 - hc_nid_c
        if year >= hc_id_new_year_c:
            fracdedc = min(fracdedc, 1.0 - hc_id_new_c)
        hc_id_nc = np.array(self.btax_params['intPaid_noncorp_hc'])[iyr]
        hc_id_new_year_nc = np.array(self.btax_params['newIntPaid_noncorp_hcyear'])[iyr]
        hc_id_new_nc = np.array(self.btax_params['newIntPaid_noncorp_hc'])[iyr]
        # Find haircut for noncorporate businesses
        if year < hc_id_new_year_nc:
            # If not subject to haircut
            fracdedn = 1.0
        else:
            # If subject to haircut
            fracdedn = 1.0 - hc_id_new_nc
        return (fracdedc, fracdedn)

    def calc_I(self, delta, r, a, b):
        """
        Calculates present value of income occuring during the period [a,b]
            delta: depreciation rate
            r: discount rate
        Note: this is based on unit income amount
        """
        if r + delta == 0:
            I = b - a
        else:
            I = (1 / (r + delta) * np.exp(-(r + delta) * a) *
                 (1 - np.exp(-(r + delta) * (b - a))))
        return I

    def calc_Ilist(self, delta, r, length=50):
        """
        Calculates present value of income unit over lifetime
            delta: depreciation rate
            r: discount rate
            length: number of periods to use
        """
        # Calculate for first (half) year
        I0 = self.calc_I(delta, r, 0, 0.5)
        Ilist = [I0]
        for j in range(1, length-1):
            Ilist.append(self.calc_I(delta, r, j-0.5, j+0.5))
        # Calculate from final period to infinity
        Ilist.append(self.calc_I(delta, r, length-1-0.5, 9e99))
        return Ilist

    def calc_F(self, f, r, i, delta, fracded, a, b):
        """
        Calculates present value of interest deduction during period [a,b]
            f: ratio of debt to assets
            r: discount rate
            i: interest rate on debt
            delta: depreciation rate
            fracded: fraction of interest paid deductible
        """
        F = (f * i / (r + delta) * fracded * np.exp(-(r + delta) * a) *
             (1 - np.exp(-(r + delta) * (b - a))))
        return F

    def calc_Flist(self, f, r, i, delta, fracded, length=50):
        """
        Calculates present value of interest deduction over lifetime
            f: ratio of debt to assets
            r: discount rate
            i: interest rate on debt
            delta: depreciation rate
            fracded: fraction of interest paid deductible
            length: number of periods to use
        """
        # Calcuate for first (half) year
        Flist = [self.calc_F(f, r, i, delta, fracded, 0, 0.5)]
        for j in range(1, length-1):
            Flist.append(self.calc_F(f, r, i, delta, fracded, j-0.5, j+0.5))
        # Calculate from final period to infinity
        Flist.append(self.calc_F(f, r, i, delta, fracded, length-1-0.5, 9e99))
        return Flist

    def calc_Dlist_exp(self, length=50):
        """
        Calculates depreciation deduction vector for expensing
        Note: by default, this is 1 for the first period and 0 thereafter
        """
        Dlist = np.zeros(length)
        Dlist[0] = 1
        return Dlist

    def calc_D_econ(self, delta, r, a, b):
        """
        Calculates PV of depreciation deduction during [a,b] using economic
        depreciation method.
            delta: depreciation rate
            r: discount rate
        """
        if r + delta == 0:
            D = delta * (b - a)
        else:
            D = (delta / (r + delta) * np.exp(-(r + delta) * a) *
                 (1 - np.exp(-(r + delta) * (b - a))))
        return D

    def calc_Dlist_econ(self, delta, r, bonus, length=50):
        """
        Calculates present value of depreciation deductions over lifetime
        for economic depreciation.
            delta: depreciation rate
            r: discount rate
            bonus: bonus depreciation rate
        """
        # Calculate for fist (half) year
        Dlist = [bonus + (1 - bonus) * self.calc_D_econ(delta, r, 0, 0.5)]
        for j in range(1, length-1):
            Dlist.append((1 - bonus) *
                         self.calc_D_econ(delta, r, j-0.5, j+0.5))
        # Calculate from last period to infinity
        Dlist.append((1 - bonus) *
                     self.calc_D_econ(delta, r, length-1-0.5, 9e99))
        return Dlist

    def calc_D_dbsl(self, N, L, r, pi, a, b):
        """
        Calculates PV of depreciation deductions during [a,b] for declining
        balance and straight-line depreciation.
            N: exponential depreciation:
                2 for double-declining balance
                1.5 for 150% declining balance
                1 for straight-line
            L: tax life
            r: discount rate
            pi: inflation rate
        """
        # Ensure N is not an int
        N = N * 1.0
        # Switching point
        t1 = L * (1 - 1 / N)
        # End of tax life
        t2 = L
        if b <= t1:
            # If entirely subject to exponential depreciation
            D = (N / L / (r + pi + N / L) * np.exp(-(r + pi + N / L) * a) *
                 (1 - np.exp(-(r + pi + N / L) * (b - a))))
        elif b <= t2:
            if a < t1:
                # If period splits exponential and straight-line depreciation
                Ddb = (N / L / (r + pi + N / L) *
                       np.exp(-(r + pi + N / L) * a) *
                       (1 - np.exp(-(r + pi + N / L) * (t1 - a))))
                if r + pi == 0:
                    # Special case of zero nominal discount rate
                    Dsl = np.exp(1 - N) * (b - t1) / (t2 - t1)
                else:
                    Dsl = (N / L / (r + pi) * np.exp(1 - N) *
                           np.exp(-(r + pi) * t1) *
                           (1 - np.exp(-(r + pi) * (b - t1))))
                D = Ddb + Dsl
            else:
                # If entirely subject to straight-line depreciation
                if r + pi == 0:
                    D = np.exp(1 - N) * (b - a) / (t2 - t1)
                else:
                    D = (N / L / (r + pi) * np.exp(1 - N) *
                         np.exp(-(r + pi) * a) *
                         (1 - np.exp(-(r + pi) * (b - a))))
        else:
            # end of period occurs after tax life ends
            if a < t2:
                # If tax life ends during period
                if r + pi == 0:
                    D = np.exp(1 - N) * (t2 - a) / (t2 - t1)
                else:
                    D = (N / L / (r + pi) * np.exp(1 - N) *
                         np.exp(-(r + pi) * a) *
                         (1 - np.exp(-(r + pi) * (t2 - a))))
            else:
                # If period occurs entirely after tax life has ended
                D = 0
        return D

    def calc_Dlist_dbsl(self, N, L, bonus, r, pi, length=50):
        """
        Calculates present value of depreciation deductions over lifetime
        for declining balance and straight-line depreciation.
            N: exponential depreciation:
                2 for double-declining balance
                1.5 for 150% declining balance
                1 for straight-line
            L: tax life
            r: discount rate
            pi: inflation rate
            length: number of periods to use
        """
        Dlist = [bonus + (1 - bonus) * self.calc_D_dbsl(N, L, r,
                                                        pi, 0, 0.5)]
        for j in range(1, length):
            Dlist.append((1 - bonus) * self.calc_D_dbsl(N, L, r,
                                                        pi, j-0.5, j+0.5))
        return Dlist

    def calc_Dlist(self, method, life, delta, r, pi, bonus, length=50):
        """
        Calculates present value of depreciation deductions over lifetime.
            method: depreciation method to use
            life: tax life
            delta: depreciation rate
            r: discount rate
            pi: inflation rate
            bonus: bonus depreciation rate
            length: number of periods to use
        """
        # Check that methods are acceptable
        assert method in ['DB 200%', 'DB 150%', 'SL',
                          'Economic', 'Expensing', 'None']
        # Check bonus depreciation rates
        assert bonus >= 0 and bonus <= 1
        if type(length) != int:
            length = int(length)
        if method == 'DB 200%':
            # Double-declining (200%) balance depreciation
            Dlist = self.calc_Dlist_dbsl(2, life, bonus, r, pi, length)
        elif method == 'DB 150%':
            # 150% declining balance depreciation
            Dlist = self.calc_Dlist_dbsl(1.5, life, bonus, r, pi, length)
        elif method == 'SL':
            # Straight-line depreciation
            Dlist = self.calc_Dlist_dbsl(1.0, life, bonus, r, pi, length)
        elif method == 'Economic':
            # Economic depreciation
            Dlist = self.calc_Dlist_econ(delta, r, bonus, length)
        elif method == 'Expensing':
            # Expensing
            Dlist = self.calc_Dlist_exp(length)
        else:
            # No depreciation
            Dlist = np.zeros(length)
        return Dlist

    def calc_Tlist(self, tdict, length=50):
        """
        Builds list of statutory tax rates for each period in lifetime
            tdict: dictionary of tax rates and when they become effective
                tdict may not be empty
                tdict must contain at least one key of '0'
                tdict keys must be as nonnegative integers
            length: number of periods to use
        """
        assert len(tdict) > 0
        # changelist is the period when the tax rate changes
        changelist = []
        for key in tdict:
            changelist.append(int(key))
        changelist.sort()
        # ratelist is list of tax rates
        ratelist = []
        for chg in changelist:
            ratelist.append(tdict[str(chg)])
        numrates = len(ratelist)
        rateind = 0
        # Get initial tax rate
        Tlist = [tdict[str(changelist[0])]]
        for j in range(1, length):
            if rateind + 1 == numrates:
                # If at end of tax rate changes
                Tlist.append(ratelist[rateind])
            else:
                if j < changelist[rateind+1]:
                    # If between tax rate changes
                    Tlist.append(ratelist[rateind])
                else:
                    # If tax rate change occurs this year
                    rateind = rateind + 1
                    Tlist.append(ratelist[rateind])
        return Tlist

    def calc_rho(self, r, pi, delta, method, life, bonus, f, rd, fracded,
                 tdict, length=50):
        """
        Calculates the cost of capital
            r: discount rate
            pi: inflation rate
            delta: depreciation rate
            method: depreciation method
            life: tax life
            bonus: bonus depreciation rate
            f: debt to asset ratio
            rd: interest rate on debt
            fracded: fraction of interest paid deductible
            tdict: dict of tax rates and changes
            length: number of periods to use
        """
        # Get tax rates for all periods
        Tlist = np.asarray(self.calc_Tlist(tdict, length))
        # Get income rates for all periods
        Nlist = np.asarray(self.calc_Ilist(delta, r, length))
        # Get depreciation deductions for all periods
        Dlist = np.asarray(self.calc_Dlist(method, life, delta,
                                           r, pi, bonus, length))
        # Get interest deductions for all periods
        Flist = np.asarray(self.calc_Flist(f, r, rd, delta, fracded, length))
        # Present value of tax shield from depreciation
        A = sum(Dlist * Tlist)
        # Present value of tax shield from interest deduction
        F = sum(Flist * Tlist)
        # Present value of gross income net-of-tax rate
        N = sum(Nlist * (1 - Tlist))
        rho = (1 - A - F) / N - delta
        return rho

    def calc_rho_inv(self, r, pi, inv_method, hold, tdict):
        """
        Calculates the cost of capital for inventories
            r: discount rate
            pi: inflation rate
            inv_method: inventory accounting method
            hold: holding period for inventories
            tdict: dict of tax rates and changes
        """
        # Acceptable inventory methods
        assert inv_method in ['FIFO', 'LIFO', 'Expensing', 'Mix']
        tau = tdict['0']
        # Cost of capital with expensing
        rho_exp = r
        # Cost of capital using LIFO
        rho_lifo = (1 / hold * np.log((np.exp((r + pi) * hold) - tau) /
                    (1 - tau)) - pi)
        # Cost of capital using FIFO
        rho_fifo = 1 / hold * np.log((np.exp(r * hold) - tau) / (1 - tau))
        if inv_method == 'FIFO':
            rho_inv = rho_fifo
        elif inv_method == 'LIFO':
            rho_inv = rho_lifo
        elif inv_method == 'Expensing':
            rho_inv = rho_exp
        else:
            # Mix of 50% FIFO and 50% LIFO
            rho_inv = 0.5 * (rho_fifo + rho_lifo)
        return rho_inv

    def calc_eatr(self, p, r, pi, delta, method, life, bonus, f, rd, fracded,
                  tdict, length=50):
        """
        Calculates the effective average tax rate on investment
            p: financial income rate
            r: discount rate
            pi: inflation rate
            delta: depreciation rate
            method: depreciation method
            life: tax life
            bonus: bonus depreciation rate
            f: debt to asset ratio
            rd: interest rate on debt
            fracded: fraction of interest paid deductible
            tdict: dict of tax rates and changes
            length: number of periods to use
        """
        # Calculate the cost of capital
        coc = self.calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded,
                            tdict, length)
        # Check that the financial income rate exceess the cost of capital
        assert p >= coc
        # Rent in the absence of tax
        Rstar = (p - r) / (r + delta)
        # Income stream
        P = p / (r + delta)
        Tlist = np.asarray(self.calc_Tlist(tdict, length))
        Nlist = np.asarray(self.calc_Ilist(delta, r, length))
        Dlist = np.asarray(self.calc_Dlist(method, life, delta,
                                           r, pi, bonus, length))
        Flist = np.asarray(self.calc_Flist(f, r, rd, delta, fracded, length))
        A = sum(Dlist * Tlist)
        F = sum(Flist * Tlist)
        N = sum(Nlist * (1 - Tlist))
        # Calculate after-tax rent
        R = -(1 - A - F) + (p + delta) * N
        eatr = (Rstar - R) / P
        return eatr

    def calc_usercost(self, r, pi, delta, method, life, bonus, f, rd, fracded,
                      tdict, length=50):
        """
        Calculates the cost of capital
            r: discount rate
            pi: inflation rate
            delta: depreciation rate
            method: depreciation method
            life: tax life
            bonus: bonus depreciation rate
            f: debt to asset ratio
            rd: interest rate on debt
            fracded: fraction of interest paid deductible
            tdict: dict of tax rates and changes
            length: number of periods to use
        """
        # Calculate the cost of capital
        coc = self.calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded,
                            tdict, length)
        ucoc = coc + delta
        return ucoc

    def calc_oneyear(self, year):
        """
        In the given year, calculates EATR and user cost of capital for each
        asset type.
        """
        # Check that year has acceptable value
        assert year in range(2017, 2028)
        # Extract economic parameters
        [r_c, r_nc, r_d, pi, f_c, f_nc] = self.get_econ_params_oneyear(year)
        # Extract tax depreciation information
        iyr = year - 1960
        Method = self.asset_c.method_history[iyr]
        Life = self.asset_c.life_history[:, iyr]
        Bonus = self.asset_c.bonus_history[:, iyr]
        # Make tax rate dictionaries
        tdict_c = self.make_tdict_c(year)
        tdict_nc = self.make_tdict_nc(year)
        # Create base DataFrame and get depreciation rates
        asset_data = copy.deepcopy(Data().taxdep_info_gross())
        asset_data.drop(['L_gds', 'L_ads', 'Method'], axis=1, inplace=True)
        Delta = np.array(asset_data['delta'])
        # Get deductible fractions of interest paid
        (fracded_c, fracded_nc) = self.calc_frac_ded(year)
        # Get inventory method
        assets = np.asarray(asset_data['Asset'])
        uc_c = np.zeros(len(assets))
        uc_nc = np.zeros(len(assets))
        eatr_c = np.zeros(len(assets))
        eatr_nc = np.zeros(len(assets))
        for j in range(len(asset_data)):
            uc_c[j] = self.calc_usercost(r_c, pi, Delta[j], Method[j],
                                         Life[j], Bonus[j], f_c, r_d,
                                         fracded_c, tdict_c, 50)
            uc_nc[j] = self.calc_usercost(r_nc, pi, Delta[j], Method[j],
                                          Life[j], Bonus[j], f_nc, r_d,
                                          fracded_nc, tdict_nc, 50)
            eatr_c[j] = self.calc_eatr(0.2, r_c, pi, Delta[j], Method[j],
                                       Life[j], Bonus[j], f_c, r_d,
                                       fracded_c, tdict_c, length=50)
            eatr_nc[j] = self.calc_eatr(0.2, r_nc, pi, Delta[j], Method[j],
                                        Life[j], Bonus[j], f_nc, r_d,
                                        fracded_nc, tdict_nc, length=50)
        # Save the results to the main DataFrame
        asset_data['uc_c'] = uc_c
        asset_data['uc_nc'] = uc_nc
        asset_data['eatr_c'] = eatr_c
        asset_data['eatr_nc'] = eatr_nc
        return asset_data

    def run_btax_mini(self, yearlist):
        """
        Runs the code to compute the user cost and EATR
        for each asset type for each year in yearlist.
        """
        basedata = copy.deepcopy(Data().taxdep_info_gross())
        basedata.drop(['L_gds', 'L_ads', 'Method'], axis=1, inplace=True)
        for year in yearlist:
            # Get calculations for each year
            results_oneyear = self.calc_oneyear(year)
            # Rename to include the year calculated
            results_oneyear.rename(columns={'uc_c': 'u_c' + str(year),
                                            'uc_nc': 'u_nc' + str(year),
                                            'eatr_c': 'eatr_c' + str(year),
                                            'eatr_nc': 'eatr_nc' + str(year)},
                                   inplace=True)
            # Merge year's results into combined DataFrame
            basedata = basedata.merge(right=results_oneyear,
                                      how='outer', on='Asset')
        return basedata
