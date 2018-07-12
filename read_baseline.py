# Read in baseline results
capPath_base_corp = pd.read_csv('capPath_base_corp.csv')
capPath_base_noncorp = pd.read_csv('capPath_base_noncorp.csv')
Kstock_base_corp = np.array(pd.read_csv('Kstock_base_corp.csv'))
Kstock_base_noncorp = np.array(pd.read_csv('Kstock_base_noncorp.csv'))
combined_base = pd.read_csv('corptax_results_base.csv')
base_params = pd.read_csv('mini_params_btax.csv')
SchC_results = pd.read_csv('SchC_base.csv')
partner_results = pd.read_csv('partnership_base.csv')
Scorp_results = pd.read_csv('Scorp_base.csv')
earnings_base = pd.read_csv('passthru_earnings.csv')
NID_base = pd.read_csv('nid_base.csv')
IntPaid_base_noncorp = pd.read_csv('int_base_noncorp.csv')
# Read in adjustment factors
adj_factors = pd.read_csv('adjfactors.csv')
adjfactor_amt_corp = adj_factors['amt'].values[0]
adjfactor_pymtc_corp = adj_factors['pymtc'].values[0]
adjfactor_ftc_corp = adj_factors['ftc'].values[0]
adjfactor_dep_corp = adj_factors['dep_corp'].values[0]
adjfactor_dep_noncorp = adj_factors['dep_noncorp'].values[0]
adjfactor_int_corp = adj_factors['int_corp'].values[0]
adjfactor_int_noncorp = adj_factors['int_noncorp'].values[0]
# Read in pass-through shares
passthru_factors = pd.read_csv('passthru_shares.csv')
depshare_scorp_posinc = passthru_factors['dep_scorp_pos'].values[0]
depshare_scorp_neginc = passthru_factors['dep_scorp_neg'].values[0]
depshare_sp_posinc = passthru_factors['dep_sp_pos'].values[0]
depshare_sp_neginc = passthru_factors['dep_sp_neg'].values[0]
depshare_partner_posinc = passthru_factors['dep_part_pos'].values[0]
depshare_partner_neginc = passthru_factors['dep_part_neg'].values[0]
intshare_scorp_posinc = passthru_factors['int_scorp_pos'].values[0]
intshare_scorp_neginc = passthru_factors['int_scorp_neg'].values[0]
intshare_sp_posinc = passthru_factors['int_sp_pos'].values[0]
intshare_sp_neginc = passthru_factors['int_sp_neg'].values[0]
intshare_partner_posinc = passthru_factors['int_part_pos'].values[0]
intshare_partner_neginc = passthru_factors['int_part_neg'].values[0]
