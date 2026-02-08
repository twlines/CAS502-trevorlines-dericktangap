"""
Test suite for PSED I/II loader and decoder. 

Tests verify 
- that the raw data files load correctly with expected dimensions
- that categorical variables decode to expected labels according to the codebook
- continuous varibable handling (e.g. missing values) is consistent with the codebook specifications
- system missing (Nan) values are preserved in the decoded data where appropriate

data source: ICPSR PSED I/II datasets, specifically the "37202-0003-Data.tsv" file which contains the raw data for analysis.
codebook reference: waves_Multi.pdf 
"""


import pytest
import pandas as pd
import numpy as np

# --- File paths (source of truth for test assertions) ---
# These paths should match the actual location of the data files used in the tests
PSED2_WAVES = 'data/37202-0003-Data.tsv'  # Raw data file for PSED II Waves dataset
PSED1_WAVES_DS3 = 'data/37203-0003-Data.tsv'  # Raw data file for PSED I Waves DS3 dataset
PSED1_WAVES_DS5 = 'data/37203-0005-Data.tsv'  # Raw data file for PSED I Waves DS5 dataset

# --- FIXTURES: LOAD EACH DATASET ONCE FOR ALL TESTS ---

@pytest.fixture(scope='module')
def psed2(): 
    """Load PSED II WAVES DATS (1,214 PANEL MEMBERS, 7821 VARIABLES)."""
    return pd.read_csv(PSED2_WAVES, sep='\t')

@pytest.fixture(scope='module')
def psed1_ds3():
    """Load PSED I WAVES DS3 DATS (1,261 PANEL MEMBERS, 5015 VARIABLES)."""
    return pd.read_csv(PSED1_WAVES_DS3, sep='\t')

@pytest.fixture(scope='module')
def psed1_ds5():
    """Load PSED I WAVES DS5 DATS (1,261 PANEL MEMBERS, 5223 VARIABLES)."""
    return pd.read_csv(PSED1_WAVES_DS5, sep='\t')



def assert_categorical_decode(df, column, codebook):
    """Helper function to assert that a categorical variable decodes correctly according to a codebook."""
    decoded = df[column].map(codebook)
    
    # raw values that exist in the codebook should decode to strings 
    known = df[column].dropna()
    known = known[known.isin(codebook.keys())]
    assert (known.map(codebook).notna()).all()

    #Nan in the raw data should stay NaN after decoding (inapplicable or missing)
    assert decoded[df[column].isna()].isna().all()

    #decoded values should only contain expected labels or NaN
    valid_labels = set(codebook.values())
    actual_labels = set(decoded.dropna().unique())
    assert actual_labels.issubset(valid_labels)



def test_load_waves_data(psed2):
    assert psed2.shape[0] == 1214
    assert psed2.shape[1] == 7821

def test_load_psed1_waves_ds3(psed1_ds3):
    assert psed1_ds3.shape[0] == 1261
    assert psed1_ds3.shape[1] == 5015


def test_load_psed1_waves_ds5(psed1_ds5):
    assert psed1_ds5.shape[0] == 1261
    assert psed1_ds5.shape[1] == 5223



def test_decode_aa4(psed2):
   
   assert_categorical_decode(psed2, 'AA4', {
        1: "Yes",
        5: "No",
        8: "Don't know",
        9: "Refused"
    })
      
    
def test_decode_be52(psed2):
    """reason for stopping venture"""
    assert_categorical_decode(psed2, 'BE52', {
        10: "Insufficient start-up funds/financing",
        11: "Bad credit; difficulty acquiring new loan",
        12: "Acquiring funds; financing (NFS)",
        19: "Other Money/Finance references",
        20: "Low demand/interest",
        21: "Low profit/revenue",
        22: "Competition too strong",
        23: "Difficulty marketing/finding customers",
        29: "Other Product/Service references",
        30: "Loss of partner/valuable employee/contact",
        31: "Loss of business location",
        32: "Poor business plan",
        33: "Government regulations",
        34: "Difficulty receiving timely payments",
        39: "Other business issue references",
        40: "Returned to previous job/occupation",
        41: "Acquired a new job/occupation",
        42: "Started new business/switched focus",
        49: "Other opportunities references",
        90: "Personal/family care issues; health",
        91: "Relocation",
        92: "Unable/unwilling to devote time",
        93: "Lack of interest/desire to continue",
        94: "Going/returning to school",
        95: "Other personal references",
        98: "Don't know", 99: "Refused",
    })

def test_decode_be56(psed2):
    """Venture status after exit. p.144 of codebook"""
    assert_categorical_decode(psed2, 'BE56', {1: "Others still working on start-up",
        2: "Others have going business",
        3: "Start-up was sold",
        4: "No longer worked on by anyone",
        8: "Don't know", 9: "Refused",
    })

def test_decode_ba50(psed2):
    """master branching variable, Codebook p. 59"""
    assert_categorical_decode(psed2, 'BA50', {
        1: "New firm", 
        2: "Active start-up",
        3: "Quit", 
    })

def test_clean_ag2(psed2):
    """Number of owners(count). Replace 98 (Don't know) and 99 (Refused) with NaN."""
    sentinels = [98, 99]
    raw = psed2["AG2"].copy()
    cleaned = raw.replace(list(sentinels), np.nan)

    assert not cleaned.dropna().isin(sentinels).any()  # No sentinel values should remain
    assert cleaned[raw.isna()].isna().all()  # NaN values should be preserved
    assert (cleaned.dropna() > 0).all()  # Valid numeric values should be non-negative


