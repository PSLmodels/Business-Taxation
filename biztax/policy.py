"""
Business-Taxation Policy class.
"""
import os
import numpy
import pandas
import taxcalc
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS


class Policy(taxcalc.Parameters):
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
        super().__init__()
        # read default parameters and initialize
        self._vals = self._params_dict_from_json_file()
        # initialize abstract base taxcalc.Parameters class
        self.initialize(START_YEAR, NUM_YEARS)
        # specify warning/error handling variables
        self.parameter_warnings = ''
        self.parameter_errors = ''
        self._ignore_errors = False

    def implement_reform(self, reform,
                         print_warnings=False, raise_errors=True):
        """
        Implement multi-year policy reform and leave current_year unchanged.

        Parameters
        ----------
        reform: dictionary of one or more YEAR:MODS pairs
            see Notes to taxcalc.Parameters _update method for info
            on MODS structure

        print_warnings: boolean
            if True, prints warnings when parameter_warnings exists;
            if False, does not print warnings when parameter_warnings exists
                    and leaves warning handling to caller of implement_reform.

        raise_errors: boolean
            if True, raises ValueError when parameter_errors exists;
            if False, does not raise ValueError when parameter_errors exists
                    and leaves error handling to caller of implement_reform.

        Raises
        ------
        ValueError:
            if reform is not a dictionary.
            if each YEAR in reform is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.
            if raise_errors is True AND
              _validate_parameter_names_types generates errors OR
              _validate_parameter_values generates errors.

        Returns
        -------
        nothing: void

        Notes
        -----
        Read taxcalc.Policy constructor Notes.
        """
        # check that all reform dictionary keys are integers
        if not isinstance(reform, dict):
            raise ValueError('ERROR: YYYY PARAM reform is not a dictionary')
        if not reform:
            return  # no reform to implement
        reform_years = sorted(list(reform.keys()))
        for year in reform_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in reform is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of remaining reform_years
        first_reform_year = min(reform_years)
        if first_reform_year < self.start_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_reform_year, self.start_year))
        if first_reform_year < self.current_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR < current_year={}'
            raise ValueError(msg.format(first_reform_year, self.current_year))
        last_reform_year = max(reform_years)
        if last_reform_year > self.end_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_reform_year, self.end_year))
        # validate reform parameter names and types
        self.parameter_warnings = ''
        self.parameter_errors = ''
        self._validate_parameter_names_types(reform)
        if not self._ignore_errors and self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # implement the reform year by year
        precall_current_year = self.current_year
        reform_parameters = set()
        for year in reform_years:
            self.set_year(year)
            reform_parameters.update(reform[year].keys())
            self._update({year: reform[year]})
        self.set_year(precall_current_year)
        # validate reform parameter values
        self._validate_parameter_values(reform_parameters)
        if self.parameter_warnings and print_warnings:
            print(self.parameter_warnings)
        if self.parameter_errors and raise_errors:
            raise ValueError('\n' + self.parameter_errors)

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

    # ----- begin private methods of Policy class -----

    def _validate_parameter_names_types(self, reform):
        """
        Check validity of parameter names and parameter types used
        in the specified reform dictionary.
        """
        param_names = set(self._vals.keys())
        for year in sorted(reform.keys()):
            for name in reform[year]:
                if name not in param_names:
                    msg = '{} {} is an unknown parameter name'
                    self.parameter_errors += (
                        'ERROR: ' + msg.format(year, name) + '\n'
                    )
                else:
                    # check parameter value type avoiding use of isinstance
                    # because isinstance(True, (int,float)) is True, which
                    # makes it impossible to check float parameters
                    valtype = self._vals[name]['value_type']
                    assert isinstance(reform[year][name], list)
                    pvalue = reform[year][name][0]
                    if isinstance(pvalue, list):
                        scalar = False  # parameter value is a list
                    else:
                        scalar = True  # parameter value is a scalar
                        pvalue = [pvalue]  # make scalar a single-item list
                    for idx in range(0, len(pvalue)):
                        if scalar:
                            pname = name
                        else:
                            pname = '{}_{}'.format(name, idx)
                        pval = pvalue[idx]
                        if valtype == 'real':
                            if type(pval) != float and type(pval) != int:
                                msg = '{} {} value {} is not a number'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
                        elif valtype == 'boolean':
                            if type(pval) != bool:
                                msg = '{} {} value {} is not boolean'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
                        elif valtype == 'integer':
                            if type(pval) != int:
                                msg = '{} {} value {} is not integer'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
                        elif valtype == 'string':
                            if type(pval) != str:
                                msg = '{} {} value {} is not a string'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
        del param_names

    def _validate_parameter_values(self, parameters_set):
        """
        Check values of parameters in specified parameter_set using
        range information from the policy_current_law.json file.
        """
        parameters = sorted(parameters_set)
        syr = self.start_year
        for pname in parameters:
            pvalue = getattr(self, pname)
            if self._vals[pname]['value_type'] == 'string':
                valid_options = self._vals[pname]['valid_values']['options']
                for idx in numpy.ndindex(pvalue.shape):
                    if pvalue[idx] not in valid_options:
                        msg = "{} {} value '{}' not in {}"
                        fullmsg = '{}: {}\n'.format(
                            'ERROR',
                            msg.format(idx[0] + syr,
                                       pname,
                                       pvalue[idx],
                                       valid_options)
                        )
                        self.parameter_errors += fullmsg
            else:  # parameter does not have string type
                for vop, vval in self._vals[pname]['valid_values'].items():
                    if isinstance(vval, str):
                        vvalue = getattr(self, vval)
                    else:
                        vvalue = numpy.full(pvalue.shape, vval)
                    assert pvalue.shape == vvalue.shape
                    assert len(pvalue.shape) <= 2
                    if len(pvalue.shape) == 2:
                        scalar = False  # parameter value is a list (vector)
                    else:
                        scalar = True  # parameter value is a scalar
                    for idx in numpy.ndindex(pvalue.shape):
                        out_of_range = False
                        if vop == 'min' and pvalue[idx] < vvalue[idx]:
                            out_of_range = True
                            msg = '{} {} value {} < min value {}'
                            extra = self._vals[pname]['invalid_minmsg']
                            if extra:
                                msg += ' {}'.format(extra)
                        if vop == 'max' and pvalue[idx] > vvalue[idx]:
                            out_of_range = True
                            msg = '{} {} value {} > max value {}'
                            extra = self._vals[pname]['invalid_maxmsg']
                            if extra:
                                msg += ' {}'.format(extra)
                        if out_of_range:
                            action = self._vals[pname]['invalid_action']
                            if scalar:
                                name = pname
                            else:
                                name = '{}_{}'.format(pname, idx[1])
                                if extra:
                                    msg += '_{}'.format(idx[1])
                            if action == 'warn':
                                fullmsg = '{}: {}\n'.format(
                                    'WARNING',
                                    msg.format(idx[0] + syr,
                                               name,
                                               pvalue[idx],
                                               vvalue[idx])
                                )
                                self.parameter_warnings += fullmsg
                            if action == 'stop':
                                fullmsg = '{}: {}\n'.format(
                                    'ERROR',
                                    msg.format(idx[0] + syr,
                                               name,
                                               pvalue[idx],
                                               vvalue[idx])
                                )
                                self.parameter_errors += fullmsg
        del parameters
