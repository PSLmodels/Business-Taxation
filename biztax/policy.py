"""
Business-Taxation Policy class.
"""
import os
import numpy
import pandas
import taxcalc as itax
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS


class Policy(itax.Policy):
    """
    Policy is a subclass of the Tax-Calculator Policy class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for the Policy class, which does not have any indexed
    policy parameters.

    Parameters:
        none
    """

    DEFAULTS_FILE_NAME = 'policy_current_law.json'
    DEFAULTS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

    def __init__(self):
        # read default parameters and initialize
        self._vals = self._params_dict_from_json_file()
        # initialize abstract base itax.Parameters class
        self.initialize(itax.Policy.JSON_START_YEAR,
                        itax.Policy.DEFAULT_NUM_YEARS)
        # specify no parameter indexing rates
        self._inflation_rates = None
        self._wage_growth_rates = None
        # specify warning/error handling variables
        self.parameter_warnings = ''
        self.parameter_errors = ''
        self._ignore_errors = False

    def parameters_dataframe(self):
        """
        Return pandas DataFrame containing all parameters in
        this Policy object (as columns) for each year (as rows)
        in the [START_YEAR, END_YEAR] range.

        But note that the returned DataFrame is indexed over the
        [0, NUM_YEARS] range (not over calendar years even though
        the DataFrame contains a year column).

        Also, note that the leading underscore character in each
        parameter name is removed in the returned DataFrame.
        """
        pdict = dict()
        btax_years = list(range(START_YEAR, END_YEAR + 1))
        pdict['year'] = btax_years
        itax_start_year = self.start_year
        itax_num_years = self.num_years
        mask = numpy.zeros(itax_num_years, dtype=bool)
        for year in btax_years:
            mask[year - itax_start_year] = True
        for pname in self._vals:
            parray = getattr(self, pname)
            pdict[pname[1:]] = parray[mask]
        return pandas.DataFrame(data=pdict)
