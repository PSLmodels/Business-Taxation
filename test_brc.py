import pandas as pd
import copy
from biztax import *
"""
from data import Data
from asset import Asset
from debt import Debt
from corporation import Corporation
from passthrough import PassThrough
from businessmodel import BusinessModel
"""

# Specify whether to overwrite results
OVERWRITE = False

# Specify defaults
btax_defaults = Data().btax_defaults

# Specify reform 1
btax_dict1 = {
        2017: {
                'tau_c': 0.3,
                'depr_3yr_method': 'GDS',
                'depr_3yr_bonus': 0.8,
                'depr_5yr_method': 'ADS',
                'depr_5yr_bonus': 0.8,
                'depr_7yr_method': 'Economic',
                'depr_7yr_bonus': 0.8,
                'depr_10yr_method': 'GDS',
                'depr_10yr_bonus': 0.6,
                'depr_15yr_method': 'Expensing',
                'depr_15yr_bonus': 0.6,
                'depr_20yr_method': 'ADS',
                'depr_20yr_bonus': 0.4,
                'depr_25yr_method': 'EconomicDS',
                'depr_25yr_bonus': 0.2,
                'depr_275yr_method': 'GDS',
                'depr_275yr_bonus': 0.2,
                'depr_39yr_method': 'ADS',
                'depr_39yr_bonus': 0.2,
                'tau_amt': 0.0,
                'pymtc_status': 1},
        2018: {
                'netIntPaid_corp_hc': 0.5,
                'sec199_hc': 0.5,
                'ftc_hc': 0.5}}
BM1 = BusinessModel(btax_dict1, {})

# Specify reform 2
btax_dict2 = {
        2017: {
                'oldIntPaid_corp_hcyear': 2017,
                'oldIntPaid_corp_hc': 0.5,
                'newIntPaid_corp_hcyear': 2017,
                'newIntPaid_corp_hc': 1.0,
                'oldIntPaid_noncorp_hcyear': 2017,
                'oldIntPaid_noncorp_hc': 0.5,
                'newIntPaid_noncorp_hcyear': 2017,
                'newIntPaid_noncorp_hc': 1.0},
        2018: {
                'undepBasis_corp_hcyear': 2018,
                'undepBasis_corp_hc': 0.5,
                'undepBasis_noncorp_hcyear': 2018,
                'undepBasis_noncorp_hc': 0.5}}
BM2 = BusinessModel(btax_dict2, {})


def test_asset0():
    """
    Test the baseline results (capital_path)
    """
    # Corporate
    asset1 = Asset(btax_defaults)
    asset1.calc_all()
    path1 = copy.deepcopy(asset1.capital_path).round(2)
    # Noncorporate
    asset2 = Asset(btax_defaults, corp=False)
    asset2.calc_all()
    path2 = copy.deepcopy(asset2.capital_path).round(2)
    if OVERWRITE:
        path1.to_csv('test_results/asset0_1.csv', index=False)
        path2.to_csv('test_results/asset0_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        path1_true = pd.read_csv('test_results/asset0_1.csv')
        path2_true = pd.read_csv('test_results/asset0_2.csv')
        testresult = path1_true.equals(path1)
        testresult *= path2_true.equals(path2)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_asset1():
    """
    Test reform 1 (capital_path)
    """
    # Corporate
    asset1 = Asset(BM1.btax_params_ref)
    asset1.calc_all()
    path1 = copy.deepcopy(asset1.capital_path).round(2)
    # Noncorporate
    asset2 = Asset(BM1.btax_params_ref, corp=False)
    asset2.calc_all()
    path2 = copy.deepcopy(asset2.capital_path).round(2)
    if OVERWRITE:
        path1.to_csv('test_results/asset1_1.csv', index=False)
        path2.to_csv('test_results/asset1_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        path1_true = pd.read_csv('test_results/asset1_1.csv')
        path2_true = pd.read_csv('test_results/asset1_2.csv')
        testresult = path1_true.equals(path1)
        testresult *= path2_true.equals(path2)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_asset2():
    """
    Test reform 2 (capital_history, capital_path)
    """# Corporate
    asset1 = Asset(BM2.btax_params_ref)
    asset1.calc_all()
    path1 = copy.deepcopy(asset1.capital_path).round(2)
    # Noncorporate
    asset2 = Asset(BM1.btax_params_ref, corp=False)
    asset2.calc_all()
    path2 = copy.deepcopy(asset2.capital_path).round(2)
    if OVERWRITE:
        path1.to_csv('test_results/asset2_1.csv', index=False)
        path2.to_csv('test_results/asset2_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        path1_true = pd.read_csv('test_results/asset2_1.csv')
        path2_true = pd.read_csv('test_results/asset2_2.csv')
        testresult = path1_true.equals(path1)
        testresult *= path2_true.equals(path2)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_debt0():
    """
    Test the baseline results (interest_path)
    """
    asset1 = Asset(btax_defaults)
    asset1.calc_all()
    asset2 = Asset(btax_defaults, corp=False)
    asset2.calc_all()
    debt1 = Debt(btax_defaults, asset1.get_forecast())
    debt2 = Debt(btax_defaults, asset2.get_forecast())
    debt1.calc_all()
    debt2.calc_all()
    path1 = copy.deepcopy(debt1.interest_path).round(2)
    path2 = copy.deepcopy(debt2.interest_path).round(2)
    if OVERWRITE:
        path1.to_csv('test_results/debt0_1.csv', index=False)
        path2.to_csv('test_results/debt0_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        path1_true = pd.read_csv('test_results/debt0_1.csv')
        path2_true = pd.read_csv('test_results/debt0_2.csv')
        testresult = path1_true.equals(path1)
        testresult *= path2_true.equals(path2)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_debt1():
    """
    Test reform 1 (interest_path)
    """
    asset1 = Asset(BM1.btax_params_ref)
    asset1.calc_all()
    asset2 = Asset(BM1.btax_params_ref, corp=False)
    asset2.calc_all()
    debt1 = Debt(BM1.btax_params_ref, asset1.get_forecast())
    debt2 = Debt(BM1.btax_params_ref, asset2.get_forecast())
    debt1.calc_all()
    debt2.calc_all()
    path1 = copy.deepcopy(debt1.interest_path).round(2)
    path2 = copy.deepcopy(debt2.interest_path).round(2)
    if OVERWRITE:
        path1.to_csv('test_results/debt1_1.csv', index=False)
        path2.to_csv('test_results/debt1_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        path1_true = pd.read_csv('test_results/debt1_1.csv')
        path2_true = pd.read_csv('test_results/debt1_2.csv')
        testresult = path1_true.equals(path1)
        testresult *= path2_true.equals(path2)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_debt2():
    """
    Test reform 2 (interest_path)
    """
    asset1 = Asset(BM2.btax_params_ref)
    asset1.calc_all()
    asset2 = Asset(BM2.btax_params_ref, corp=False)
    asset2.calc_all()
    debt1 = Debt(BM2.btax_params_ref, asset1.get_forecast())
    debt2 = Debt(BM2.btax_params_ref, asset2.get_forecast())
    debt1.calc_all()
    debt2.calc_all()
    path1 = copy.deepcopy(debt1.interest_path).round(2)
    path2 = copy.deepcopy(debt2.interest_path).round(2)
    if OVERWRITE:
        path1.to_csv('test_results/debt2_1.csv', index=False)
        path2.to_csv('test_results/debt2_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        path1_true = pd.read_csv('test_results/debt2_1.csv')
        path2_true = pd.read_csv('test_results/debt2_2.csv')
        testresult = path1_true.equals(path1)
        testresult *= path2_true.equals(path2)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_corporation0():
    """
    Test the baseline results (real_results, taxreturn.combined_return)
    """
    corp1 = Corporation(btax_defaults)
    corp1.calc_static()
    real1 = copy.deepcopy(corp1.real_results).round(2)
    tax1 = copy.deepcopy(corp1.taxreturn.combined_return).round(2)
    if OVERWRITE:
        real1.to_csv('test_results/corp0_1.csv', index=False)
        tax1.to_csv('test_results/corp0_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        real1_true = pd.read_csv('test_results/corp0_1.csv')
        tax1_true = pd.read_csv('test_results/corp0_2.csv')
        testresult = real1_true.equals(real1)
        testresult *= tax1_true.equals(tax1)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_corporation1():
    """
    Test reform 1 (real_results, taxreturn.combined_return)
    """
    corp1 = Corporation(BM1.btax_params_ref)
    corp1.calc_static()
    real1 = copy.deepcopy(corp1.real_results).round(2)
    tax1 = copy.deepcopy(corp1.taxreturn.combined_return).round(2)
    if OVERWRITE:
        real1.to_csv('test_results/corp1_1.csv', index=False)
        tax1.to_csv('test_results/corp1_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        real1_true = pd.read_csv('test_results/corp1_1.csv')
        tax1_true = pd.read_csv('test_results/corp1_2.csv')
        testresult = real1_true.equals(real1)
        testresult *= tax1_true.equals(tax1)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_corporation2():
    """
    Test reform 2 (real_results, taxreturn.combined_return)
    """
    corp1 = Corporation(BM2.btax_params_ref)
    corp1.calc_static()
    real1 = copy.deepcopy(corp1.real_results).round(2)
    tax1 = copy.deepcopy(corp1.taxreturn.combined_return).round(2)
    if OVERWRITE:
        real1.to_csv('test_results/corp2_1.csv', index=False)
        tax1.to_csv('test_results/corp2_2.csv', index=False)
        message = "OVERWRITTEN"
    else:
        real1_true = pd.read_csv('test_results/corp2_1.csv')
        tax1_true = pd.read_csv('test_results/corp2_2.csv')
        testresult = real1_true.equals(real1)
        testresult *= tax1_true.equals(tax1)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_passthrough0():
    """
    Test the baseline results (SchC_results, partner_results, Scorp_results)
    """
    pt1 = PassThrough(btax_defaults)
    pt1.calc_static()
    SchC = copy.deepcopy(pt1.SchC_results).round(2)
    partner = copy.deepcopy(pt1.partner_results).round(2)
    Scorp = copy.deepcopy(pt1.Scorp_results).round(2)
    if OVERWRITE:
        SchC.to_csv('test_results/passthrough0_1.csv', index=False)
        partner.to_csv('test_results/passthrough0_2.csv', index=False)
        Scorp.to_csv('test_results/passthrough0_3.csv', index=False)
        message = "OVERWRITTEN"
    else:
        SchC_true = pd.read_csv('test_results/passthrough0_1.csv')
        partner_true = pd.read_csv('test_results/passthrough0_2.csv')
        Scorp_true = pd.read_csv('test_results/passthrough0_3.csv')
        testresult = SchC_true.equals(SchC)
        testresult *= partner_true.equals(partner)
        testresult *= Scorp_true.equals(Scorp)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_passthrough1():
    """
    Test reform 1 (SchC_results, partner_results, Scorp_results)
    """
    pt1 = PassThrough(BM1.btax_params_ref)
    pt1.calc_static()
    SchC = copy.deepcopy(pt1.SchC_results).round(2)
    partner = copy.deepcopy(pt1.partner_results).round(2)
    Scorp = copy.deepcopy(pt1.Scorp_results).round(2)
    if OVERWRITE:
        SchC.to_csv('test_results/passthrough1_1.csv', index=False)
        partner.to_csv('test_results/passthrough1_2.csv', index=False)
        Scorp.to_csv('test_results/passthrough1_3.csv', index=False)
        message = "OVERWRITTEN"
    else:
        SchC_true = pd.read_csv('test_results/passthrough1_1.csv')
        partner_true = pd.read_csv('test_results/passthrough1_2.csv')
        Scorp_true = pd.read_csv('test_results/passthrough1_3.csv')
        testresult = SchC_true.equals(SchC)
        testresult *= partner_true.equals(partner)
        testresult *= Scorp_true.equals(Scorp)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_passthrough2():
    """
    Test reform 2 (real_results, SchC_results, partner_results, Scorp_results)
    """
    pt1 = PassThrough(BM2.btax_params_ref)
    pt1.calc_static()
    SchC = copy.deepcopy(pt1.SchC_results).round(2)
    partner = copy.deepcopy(pt1.partner_results).round(2)
    Scorp = copy.deepcopy(pt1.Scorp_results).round(2)
    if OVERWRITE:
        SchC.to_csv('test_results/passthrough2_1.csv', index=False)
        partner.to_csv('test_results/passthrough2_2.csv', index=False)
        Scorp.to_csv('test_results/passthrough2_3.csv', index=False)
        message = "OVERWRITTEN"
    else:
        SchC_true = pd.read_csv('test_results/passthrough2_1.csv')
        partner_true = pd.read_csv('test_results/passthrough2_2.csv')
        Scorp_true = pd.read_csv('test_results/passthrough2_3.csv')
        testresult = SchC_true.equals(SchC)
        testresult *= partner_true.equals(partner)
        testresult *= Scorp_true.equals(Scorp)
        if testresult:
            message = "PASS"
        else:
            message = "FAIL"
    return message

def test_response0():
    """
    Test the baseline results with nonzero elasticities
    """
    return None

def test_response1a():
    """
    Test reform 1 with zero elasticities
    """
    return None

def test_response1b():
    """
    Test reform 1 with nonzero elasticities
    """
    return None

def test_response2():
    """
    Test reform 2 with nonzero elasticities
    """
    return None

def test_businessmodel():
    """
    Tests the results of the 3 BusinessModel objects
    """
    return None
    



mA0 = test_asset0()
mA1 = test_asset1()
mA2 = test_asset2()
mD0 = test_debt0()
mD1 = test_debt1()
mD2 = test_debt2()
mC0 = test_corporation0()
mC1 = test_corporation1()
mC2 = test_corporation2()
mP0 = test_passthrough0()
mP1 = test_passthrough1()
mP2 = test_passthrough2()
test_response0()
test_response1a()
test_response1b()
test_response2()
test_businessmodel()


print("Test Asset 0: " + mA0)
print("Test Asset 1: " + mA1)
print("Test Asset 2: " + mA2)
print("Test Debt 0: " + mD0)
print("Test Debt 1: " + mD1)
print("Test Debt 2: " + mD2)
print("Test Corporation 0: " + mC0)
print("Test Corporation 1: " + mC1)
print("Test Corporation 2: " + mC2)
print("Test PassThrough 0: " + mP0)
print("Test PassThrough 1: " + mP1)
print("Test PassThrough 2: " + mP2)




