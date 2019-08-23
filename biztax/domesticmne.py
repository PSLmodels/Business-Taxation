import numpy as np
import pandas as pd
import copy
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.cfc import CFC


class DomesticMNE():
    """
    Constructor for the DomesticMNE class.
    This contains information for source of profits and foreign taxes for
    domestic-headquartered multinational enterprises.
    """

    def __init__(self, btax_params, data=None):
        # Store policy parameter object
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        # Create Data object
        if data is None:
            self.data = Data()
        elif isinstance(data, Data):
            self.data = data
        else:
            raise ValueError('data must be a Data object')
        # Extract baseline forecast for earnings and action
        self.dmne_data = copy.deepcopy(self.data.dmne_data)
        # Create affiliated CFC
        self.cfc = CFC(self.btax_params)

    def create_earnings(self):
        """
        Create underlying earnings forecast for MNE,
        excluding CFC.
        """
        # Growth factors for foreign profits
        earnings_forecast = np.asarray(self.data.gfactors['profit_f'])[1:]
        # Get income and deduction amounts for 2014
        div_noncfc14 = np.asarray(self.dmne_data['div_noncfc'])[0]
        interest14 = np.asarray(self.dmne_data['interest'])[0]
        rent14 = np.asarray(self.dmne_data['rent'])[0]
        serviceinc14 = np.asarray(self.dmne_data['service'])[0]
        branchinc14 = np.asarray(self.dmne_data['branch'])[0]
        otherinc14 = np.asarray(self.dmne_data['otherinc'])[0]
        foreigntax14 = np.asarray(self.dmne_data['ftaxpaid'])[0]
        deductions14 = np.asarray(self.dmne_data['deductions'])[0]
        adjustments14 = np.asarray(self.dmne_data['adjustments'])[0]
        # Forecast these for 2014-2027
        div_noncfc = div_noncfc14 * earnings_forecast / earnings_forecast[0]
        interest = interest14 * earnings_forecast / earnings_forecast[0]
        rent = rent14 * earnings_forecast / earnings_forecast[0]
        serviceinc = serviceinc14 * earnings_forecast / earnings_forecast[0]
        branchinc = branchinc14 * earnings_forecast / earnings_forecast[0]
        otherinc = otherinc14 * earnings_forecast / earnings_forecast[0]
        foreigntax = foreigntax14 * earnings_forecast / earnings_forecast[0]
        deductions = deductions14 * earnings_forecast / earnings_forecast[0]
        adjustments = adjustments14 * earnings_forecast / earnings_forecast[0]
        # Combine in relevant tax categories
        self.divinc = div_noncfc + self.cfc.dividends
        self.otherinc = (interest + rent + serviceinc + branchinc + otherinc -
                         deductions - adjustments)
        self.foreigntax = foreigntax
        self.repatinc = self.cfc.repatriations

    def taxable_earnings(self):
        """
        Compute income from foreign corporations included in taxable income.
        """
        divtinc = self.divinc * np.asarray(self.btax_params['foreign_dividend_inclusion'])
        grosstax = self.foreigntax *  np.asarray(self.btax_params['foreign_tax_grossrt'])
        repattinc = self.repatinc * np.asarray(self.btax_params['foreign_repatriation_inclusion'])
        self.taxinc = (divtinc + grosstax + repattinc
                       + self.cfc.subpartF + self.cfc.GILTI_tinc)

    def calcFTC(self):
        """
        Calculates foreign tax credit for [START_YEAR, END_YEAR].
        Note: This should be replaced as the MNE model is improved.
        """
        hclist = np.array(self.btax_params['ftc_hc'])

        def calcWAvgTaxRate(year):
            """
            Calculates the weighted average statutory corporate tax rate
            in all OECD countries in a given year.
            """
            assert year in range(1995, END_YEAR+1)
            year = min(year, 2016)
            gdp_list = np.asarray(self.data.ftc_gdp_data[str(year)])
            taxrate_list = np.asarray(self.data.ftc_taxrates_data[str(year)])
            # remove observations with missing data
            taxrate_list2 = np.where(np.isnan(taxrate_list), 0, taxrate_list)
            gdp_list2 = np.where(np.isnan(taxrate_list), 0, gdp_list)
            avgrate = sum(taxrate_list2 * gdp_list2) / sum(gdp_list2)
            return avgrate

        # Get foreign profits forecast
        profits = np.asarray(self.data.ftc_other_data['C_total'][19:])
        profits_d = np.asarray(self.data.ftc_other_data['C_domestic'][19:])
        tax_f = np.zeros(NUM_YEARS)
        for iyr in range(NUM_YEARS):
            tax_f[iyr] = calcWAvgTaxRate(iyr + START_YEAR)
        ftc_final = ((profits - profits_d) * tax_f / 100. *
                     self.data.adjfactor_ftc_corp *
                     (1 - hclist)) * self.data.rescale_corp
        self.ftc = ftc_final

    def calc_all(self):
        """
        Run all calculations for the DomesticMNE.
        """
        self.cfc.calc_all()
        self.create_earnings()
        self.taxable_earnings()
        self.calcFTC()
        # Store results in DataFrame
        self.dmne_results = pd.DataFrame({'year': range(START_YEAR, END_YEAR+1),
                                          'foreign_directinc': self.otherinc,
                                          'foreign_indirectinc': (self.divinc +
                                                                  self.cfc.subpartF),
                                          'foreign_tax': self.foreigntax,
                                          'foreign_taxinc': self.taxinc,
                                          'ftc': self.ftc})

    def update_investment(self):
        """
        Updates investment location (not total) based on response.
        Not yet built.
        """
        return None

    def update_profits(self, repat_response):
        """
        Updates location of profits based on profit-shifting response and
        repatriation rate from profits in CFC.
        Currently, only handles the repatriation response.
        """
        self.cfc.update_cfc(repat_response)
