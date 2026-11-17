import pytest
import pandas as pd
from decimal import Decimal
from io import StringIO
from app.services.reconciliation_engine import ReconciliationEngine
from app.services.sample_data_generator import generate_sample_data
from app.utils.money import parse_money


@pytest.fixture
def engine():
    return ReconciliationEngine(tolerance="0.01")


@pytest.fixture
def sample_data():
    return generate_sample_data()


@pytest.fixture
def sample_dfs(sample_data):
    txn_df = pd.read_csv(StringIO(sample_data["transactions_csv"]))
    stl_df = pd.read_csv(StringIO(sample_data["settlements_csv"]))
    return txn_df, stl_df


def make_txn_df(rows):
    """Helper to create transaction DataFrame from list of dicts."""
    return pd.DataFrame(rows)


def make_stl_df(rows):
    """Helper to create settlement DataFrame from list of dicts."""
    return pd.DataFrame(rows)
