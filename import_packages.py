# This file imports all necessary packages
import taxcalc
from taxcalc import *
import btax
from btax.run_btax import run_btax, run_btax_with_baseline_delta
import pandas as pd
import numpy as np
import copy
import math
if track_progress:
    print "All packages successfully imported"
"""
Set defauls for various repeals and other provisions
Note that these must be constant after implementation.
"""
brc_defaults_other = {
    'undepBasis_corp_hc': {0: 0.0},
    'undepBasis_noncorp_hc': {0: 0.0},
    'amt_repeal': {9e99: False},
    'pymtc_repeal': {9e99: False},
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
