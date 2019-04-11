"""
Business-Taxation Policy class.
"""
import os
import pandas
import taxcalc
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS


class Policy(taxcalc.Parameters):
    """
    The Policy class is derived from the Tax-Calculator Parameters class,
    and therefore, inherits its methods (none of which are shown here).

    Constructor for the Business-Taxation Policy class, which
    does not have any (wage or price) indexed parameters and
    does not have any vector parameters.

    Parameters:
        none
    """

    DEFAULTS_FILE_NAME = 'policy_current_law.json'
    DEFAULTS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

    def __init__(self):
        # read default parameters and initialize
        super().__init__()
        self.initialize(START_YEAR, NUM_YEARS)

    def implement_reform(self, reform,
                         print_warnings=True, raise_errors=True):
        """
        Implement specified policy reform and leave current_year unchanged.
        (see taxcalc.Parameters._update for argument documentation.)
        """
        self._update(reform, print_warnings, raise_errors)

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
        for pname in self._vals:
            parray = getattr(self, pname)
            pdict[pname[1:]] = parray
        return pandas.DataFrame(data=pdict)
