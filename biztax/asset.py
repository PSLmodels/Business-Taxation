"""
Business-Taxation Asset class.
"""
import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS, HISTORY_START
from biztax.data import Data


class Asset():
    """
    Constructor for the Asset class.
    This class includes several objects related to assets and depreciation:
        For internal class use:
            investment_history:
                array of investment amounts
                asset type (95) x year investment made (68)
            capital_history:
                array of asset amounts
                asset type (95) x years in the budget window (NUM_YEARS)
            system_history:
                array of depreciation systems (GDS or ADS)
                asset type (95) x year investment made (68)
            method_history:
                array of depreciation methods (DB, Economics, etc.)
                asset type (95) x year investment made (68)
            life_history:
                array of tax lives (see LIVES list)
                asset type (95) and year investment made (68) given system
            bonus_history:
                array of effective bonus depreciation rates
                asset type (95) x year investment made (68)
            ccr_data:
                DataFrame of asset amounts and economic depreciation rates
                asset type (95), 2017 only
            capital_path:
                DataFrame of asset information totals in the budget window

    Parameters:
        corp: True for corporate, False for noncorporate
        btax_params: dict of business tax policy parameters
        response: DataFrame of investment responses
    """

    def __init__(self, btax_params, corp=True, data=None, response=None):
        # Create an associated Data object
        if isinstance(data, Data):
            self.data = data
        else:
            self.data = Data()
        # Check inputs
        if isinstance(corp, bool):
            self.corp = corp
        else:
            raise ValueError('corp must be True or False')
        if response is None or isinstance(response, pd.DataFrame):
            self.response = response
        else:
            raise ValueError('response must be DataFrame or None')
        if corp:
            self.adjustments = {'bonus': 0.60290131, 'sec179': 0.016687178,
                                'rescalar': self.data.rescale_corp}
        else:
            self.adjustments = {'bonus': 0.453683778, 'sec179': 0.17299506,
                                'rescalar': self.data.rescale_noncorp}
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')

    def update_response(self, response):
        """
        Updates the response DataFrame.
        Note: The response is the investment response DataFrame, not a
              Response object.
        """
        assert isinstance(response, pd.DataFrame)
        self.response = response

    def build_inv_matrix(self):
        """
        Builds investment array by asset type and by year made
        """
        # Get historical investment for 1960-2014
        if self.corp:
            investment_df = copy.deepcopy(self.data.investment_corp)
        else:
            investment_df = copy.deepcopy(self.data.investment_noncorp)
        # Extend investment using NGDP (growth factors from CBO forecast)
        for year in range(START_YEAR + 1, END_YEAR + 1):
            gfact = (self.data.investmentGfactors_data['ngdp'][year-HISTORY_START]
                     / self.data.investmentGfactors_data['ngdp'][54])
            investment_df[str(year)] = investment_df[str(START_YEAR)] * gfact
        # Update investment matrix to include investment responses
        if self.response is not None:
            if self.corp:
                deltaIkey = 'deltaIc'
            else:
                deltaIkey = 'deltaInc'
            for year in range(START_YEAR, END_YEAR + 1):
                investment_df[str(year)] = (investment_df[str(year)] *
                                            (1. + self.response[deltaIkey + str(year)]))
        self.investment_history = investment_df

    def build_deprLaw_matrices(self):
        """
        Builds the arrays for tax depreciation laws
        """
        def taxdep_final(depr_methods, depr_bonuses):
            """
            Constructs the DataFrame of information for tax depreciation.
            Only relevant for years beginning with START_YEAR.
            Returns a DataFrame with:
                depreciation method,
                tax depreciation life,
                true depreciation rate,
                bonus depreciation rate.
            """
            taxdep = copy.deepcopy(self.data.taxdep_info_gross())
            system = np.asarray(taxdep['System'])
            life = np.asarray(taxdep['L_gds'])
            # Determine depreciation systems for each asset class (by GDS life)
            for cl, method in depr_methods.items():
                system[life == cl] = method
            # Determine tax life
            L_ads = np.asarray(taxdep['L_ads'])
            Llist = np.asarray(taxdep['L_gds'])
            Llist[system == 'ADS'] = L_ads[system == 'ADS']
            Llist[system == 'None'] = 9e99
            taxdep['L'] = Llist
            # Determine depreciation method. Default is GDS method
            method = np.asarray(taxdep['Method'])
            for i in range(len(method)):
                if system[i] == 'ADS':
                    method[i] = np.asarray(taxdep['ADS method'])[i]
                elif system[i] == 'Economic':
                    method[i] = 'Economic'
                elif system[i] == 'None':
                    method[i] = 'None'
                elif system[i] == 'Expensing':
                    method[i] = 'Expensing'
                elif system[i] != 'GDS':
                    asset1 = np.asarray(taxdep['Asset'])[i]
                    raise ValueError('Must specify depreciation system for '
                                     + asset1 + '. Cannot use ' + str(system[i]))
            taxdep['Method'] = method
            # Detemine bonus depreciation rate
            bonus = np.zeros(len(taxdep))
            for cl, cl_bonus in depr_bonuses.items():
                bonus[life == cl] = cl_bonus
            taxdep['bonus'] = bonus
            taxdep.drop(['L_gds', 'L_ads', 'Class life'],
                        axis=1, inplace=True)
            return taxdep

        def taxdep_preset(year):
            """
            Constructs the DataFrame of information for tax depreciation.
            Only relevant for years before START_YEAR.
            Returns a DataFrame with:
                depreciation method,
                tax depreciation life,
                true depreciation rate,
                bonus depreciation rate.
            """
            taxdep = copy.deepcopy(self.data.taxdep_info_gross())
            taxdep['L'] = taxdep['L_gds']
            life = np.asarray(taxdep['L_gds'])
            bonus = np.zeros(len(life))
            for y in [3, 5, 7, 10, 15, 20, 25, 27.5, 39]:
                s = "bonus{}".format(y if y != 27.5 else 27)
                bonus[life == y] = self.data.bonus_data[s][year - HISTORY_START]
            taxdep['bonus'] = bonus
            taxdep.drop(['L_gds', 'L_ads', 'Class life'],
                        axis=1, inplace=True)
            return taxdep

        def get_btax_params_oneyear(btax_params, year):
            """
            Extracts tax depreciation parameters and
            calls the functions to build the tax depreciation
            DataFrames.
            """
            if year >= START_YEAR:
                year = min(year, END_YEAR)
                iyr = year - START_YEAR
                depr_methods = {}
                depr_bonuses = {}
                for y in [3, 5, 7, 10, 15, 20, 25, 27.5, 39]:
                    s = "depr_{}yr_".format(y if y != 27.5 else 275)
                    depr_methods[y] = btax_params[s + 'method'][iyr]
                    depr_bonuses[y] = btax_params[s + 'bonus'][iyr]
                taxdep = taxdep_final(depr_methods, depr_bonuses)
            else:
                taxdep = taxdep_preset(year)
            return taxdep
        """
        Create arrays and store depreciation rules in them
        """
        method_history = [[]] * 68
        life_history = np.zeros((95, 68))
        bonus_history = np.zeros((95, 68))
        for year in range(HISTORY_START, END_YEAR + 1):
            iyr = year - HISTORY_START
            params_oneyear = get_btax_params_oneyear(self.btax_params, year)
            method_history[iyr] = params_oneyear['Method']
            life_history[:, iyr] = params_oneyear['L']
            bonus_history[:, iyr] = params_oneyear['bonus']
        self.method_history = method_history
        self.life_history = life_history
        self.bonus_history = bonus_history

    def calcDep_oneyear(self, year):
        """
        Calculates total depreciation deductions taken in the year.
        """
        def depreciationDeduction(year_investment, year_deduction,
                                  method, L, delta, bonus):
            """
            Computes the nominal depreciation deduction taken on any
            unit investment in any year with any depreciation method and life.
            Parameters:
                year_investment: year the investment is made
                year_deduction: year the CCR deduction is taken
                method: method of CCR (DB 200%, DB 150%, SL, Expensing, None)
                L: class life for DB or SL depreciation (MACRS)
                delta: economic depreciation rate
                bonus: bonus depreciation rate
            """
            assert method in ['DB 200%', 'DB 150%', 'SL',
                              'Expensing', 'Economic', 'None']
            # No depreciation
            if method == 'None':
                deduction = 0
            # Expensing
            elif method == 'Expensing':
                if year_deduction == year_investment:
                    deduction = 1.0
                else:
                    deduction = 0
            # Economic depreciation
            elif method == 'Economic':
                yded = year_deduction
                pi_temp = (
                    self.data.investmentGfactors_data['pce'][yded + 1]
                    / self.data.investmentGfactors_data['pce'][yded]
                )
                if pi_temp == np.exp(delta):
                    annual_change = 1.0
                else:
                    if year_deduction == year_investment:
                        annual_change = (
                            ((pi_temp * np.exp(delta / 2)) ** 0.5 - 1)
                            / (np.log(pi_temp - delta))
                        )
                    else:
                        annual_change = (
                            (pi_temp * np.exp(delta) - 1)
                            / (np.log(pi_temp) - delta)
                        )

                if year_deduction < year_investment:
                    sval = 0
                    deduction = 0
                elif year_deduction == year_investment:
                    sval = 1.0
                    deduction = (
                        bonus + (1 - bonus) * delta * sval * annual_change
                    )
                else:
                    sval = (np.exp(-delta * (year_deduction - year_investment)) *
                            self.data.investmentGfactors_data['pce'][year_deduction] / 2.0 /
                            (self.data.investmentGfactors_data['pce'][year_investment] +
                             self.data.investmentGfactors_data['pce'][year_investment + 1]))
                    deduction = (1 - bonus) * delta * sval * annual_change
            else:
                if method == 'DB 200%':
                    N = 2
                elif method == 'DB 150%':
                    N = 1.5
                elif method == 'SL':
                    N = 1

            # DB or SL depreciation, half-year convention
                t0 = year_investment + 0.5
                t1 = t0 + L * (1 - 1 / N)
                s1 = year_deduction
                s2 = s1 + 1
                if year_deduction < year_investment:
                    deduction = 0
                elif year_deduction > year_investment + L:
                    deduction = 0
                elif year_deduction == year_investment:
                    deduction = (
                        bonus + (1 - bonus) * (1 - np.exp(-N / L * 0.5))
                    )
                elif s2 <= t1:
                    deduction = ((1 - bonus) * (np.exp(-N / L * (s1 - t0)) -
                                                np.exp(-N / L * (s2 - t0))))
                elif s1 >= t1 and s1 <= t0 + L and s2 > t0 + L:
                    deduction = (
                        (1 - bonus) * (N / L * np.exp(1 - N)
                                       * (s2 - s1) * 0.5)
                    )
                elif s1 >= t1 and s2 <= t0 + L:
                    deduction = (
                        (1 - bonus) * (N / L * np.exp(1 - N) * (s2 - s1))
                    )
                elif s1 < t1 and s2 > t1:
                    deduction = (
                        (1 - bonus) * (np.exp(-N / L * (s1 - t0)) -
                                       np.exp(-N / L * (t1 - t0)) +
                                       N / L * np.exp(1 - N) * (s2 - t1))
                    )
            return deduction

        """
        Calculate depreciation deductions for each year
        """
        unitDep_arr = np.zeros((95, 68))
        delta = np.asarray(self.data.taxdep_info_gross()['delta'])
        for i in range(95):
            # Iterate over asset types
            for j in range(68):
                # Iterate over investment years
                bonus1 = min((self.bonus_history[i, j]
                              * self.adjustments['bonus']
                              + self.adjustments['sec179']), 1.0)
                unitDep_arr[i, j] = depreciationDeduction(
                    j, year - HISTORY_START, self.method_history[j][i],
                    self.life_history[i, j], delta[i], bonus1
                )
        inv_hist = copy.deepcopy(self.investment_history)
        inv_hist.drop(['asset_code'], axis=1, inplace=True)
        inv_hist2 = inv_hist.to_numpy()
        Dep_arr = inv_hist2 * unitDep_arr
        # Apply the haircut on undepreciated basis
        iyr = year - START_YEAR
        if year < START_YEAR:
            # Use no haircut for years before calculator
            hc_undep_year = 0
            hc_undep = 0.
        else:
            if self.corp:
                hc_undep_year = np.array(self.btax_params['undepBasis_corp_hcyear'])[iyr]
                hc_undep = np.array(self.btax_params['undepBasis_corp_hc'])[iyr]
            else:
                hc_undep_year = np.array(self.btax_params['undepBasis_noncorp_hcyear'])[iyr]
                hc_undep = np.array(self.btax_params['undepBasis_noncorp_hc'])[iyr]
        if year >= hc_undep_year:
            for j in range(68):
                if j < hc_undep_year:
                    Dep_arr[:, j] = Dep_arr[:, j] * (1 - hc_undep)
        # Asset types included in tax depreciation or not
        other_assets = [68, 69, 70] # Software
        other_assets.extend(range(71, 86)) # Add R&D categories
        depr_assets = list(range(0, 68)) # Tangible assets
        depr_assets.extend(range(86, 95)) # Add artistic originals
        depr_assets.append(93) # Add residential
        # Tax depreciation deduction
        depded = Dep_arr[depr_assets,:].sum().sum()
        # Other CCR deduction
        otherded = Dep_arr[other_assets,:].sum().sum()
        return [depded, otherded]

    def calcDep_allyears(self):
        """
        Calculates total depreciation deductions taken for all years
        1960-2035.
        """
        dep_deductions = np.zeros(END_YEAR + 1 - HISTORY_START)
        for year in range(HISTORY_START, END_YEAR + 1):
            dep_deductions[year - HISTORY_START] = self.calcDep_oneyear(year)[0]
        return dep_deductions

    def calcDep_budget(self):
        """
        Calculates total depreciation deductions taken for START_ to END_YEAR.
        """
        dep_deductions = np.zeros(NUM_YEARS)
        other_deductions = np.zeros(NUM_YEARS)
        for iyr in range(0, NUM_YEARS):
            year = iyr + START_YEAR
            [depded, otherded] = self.calcDep_oneyear(year)
            dep_deductions[iyr] = depded
            other_deductions[iyr] = otherded
        return dep_deductions

    def build_capital_history(self):
        """
        Builds capital history array using investment_history and capital_df
        """
        # Get historical capital stock
        if self.corp:
            capital_df1 = copy.deepcopy(self.data.capital_corp)
        else:
            capital_df1 = copy.deepcopy(self.data.capital_noncorp)
        capital_df1.rename(columns={'asset_code': 'Code'}, inplace=True)
        capital_df2 = capital_df1.merge(right=self.data.econ_depr_df(),
                                        how='outer', on='Code')
        trueDep_df = copy.deepcopy(self.data.econ_depr_df())
        pcelist = np.asarray(self.data.investmentGfactors_data['pce'])
        for year in range(START_YEAR, END_YEAR + 1):
            trueDep_df[str(year)] = capital_df2[str(year)] * trueDep_df['delta']
            capital_df2[str(year + 1)] = ((capital_df2[str(year)]
                                           - trueDep_df[str(year)]
                                           + self.investment_history[str(year)])
                                          * pcelist[year-HISTORY_START+1]
                                          / pcelist[year-HISTORY_START])
        self.capital_history = capital_df2
        self.trueDep = trueDep_df

    def build_capital_path(self):
        """
        Builds the DataFrame of asset amount, investment and depreciation
        totals for each year in the budget window.
        """
        # Sum across assets and put into new dataset
        Kstock_total = np.zeros(NUM_YEARS)
        trueDep_total = np.zeros(NUM_YEARS)
        inv_total = np.zeros(NUM_YEARS)
        Mdep_total = np.zeros(NUM_YEARS)
        Oded_total = np.zeros(NUM_YEARS)
        for year in range(START_YEAR, END_YEAR + 1):
            iyr = year - START_YEAR
            adjfactor = self.adjustments['rescalar'][iyr]
            Kstock_total[iyr] = sum(self.capital_history[str(year)]) * adjfactor
            trueDep_total[iyr] = sum(self.trueDep[str(year)]) * adjfactor
            inv_total[iyr] = sum(self.investment_history[str(year)]) * adjfactor
            [depded, otherded] = self.calcDep_oneyear(year)
            Mdep_total[iyr] = depded * adjfactor
            Oded_total[iyr] = otherded * adjfactor
        cap_result = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                   'Kstock': Kstock_total,
                                   'Investment': inv_total,
                                   'trueDep': trueDep_total,
                                   'taxDep': Mdep_total,
                                   'otherCCR': Oded_total})
        self.capital_path = cap_result

    def calc_all(self):
        """
        Executes all calculations for Asset object.
        """
        self.build_inv_matrix()
        self.build_deprLaw_matrices()
        self.build_capital_history()
        self.build_capital_path()
        return None

    def get_forecast(self):
        """
        Returns an array of the capital stock for [START_YEAR, END_YEAR]
        """
        forecast = np.array(self.capital_path['Kstock'])
        return forecast

    def get_taxdep(self):
        """
        Returns an array of tax depreciation deductions for
        [START_YEAR, END_YEAR]
        """
        taxdep = np.array(self.capital_path['taxDep'])
        return taxdep

    def get_investment(self):
        """
        Returns an array of total investment for [START_YEAR, END_YEAR]
        """
        inv1 = np.array(self.capital_path['Investment'])
        return inv1

    def get_truedep(self):
        """
        Returns an array of true depreciation for [START_YEAR, END_YEAR]
        """
        truedep = np.array(self.capital_path['trueDep'])
        return truedep
