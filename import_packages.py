# This file imports all necessary packages
import taxcalc
from taxcalc import *
import pandas as pd
import numpy as np
import copy
import math
import csv
import scipy.optimize
if track_progress:
    print("All packages successfully imported")
"""
Set defauls for various repeals and other provisions
Note that these must be constant after implementation.
"""
brc_defaults_other = {
    'undepBasis_corp_hc': {0: 0.0},
    'undepBasis_noncorp_hc': {0: 0.0},
    'ftc_hc': {9e99: 0.0},
    'sec199_hc': {9e99: 0.0},
    'oldIntPaid_corp_hc': {0: 0.0},
    'newIntPaid_corp_hc': {0: 0.0},
    'netIntPaid_corp_hc': {0: 0.0},
    'oldIntPaid_noncorp_hc': {0: 0.0},
    'newIntPaid_noncorp_hc': {0: 0.0},
    'reclassify_taxdep_gdslife': {9e99: {}},
    'reclassify_taxdep_adslife': {9e99: {}}
}
