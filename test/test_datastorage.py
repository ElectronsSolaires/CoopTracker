from datetime import  date
import test.config_test as cfg
import datastorage

import pytest

prod_file_path = "./Raw/"      #tell where production files are stored

def test_with_missing_files():
    # test basic functionality
    start_date = date(2022,2,10)
    end_date = date(2022,2,18)
    datastorage.get_data_prod_hist_day(start_date, end_date, None, 'T0102', prod_file_path, cfg)

def test_with_partial_none_values():
    # test basic functionality
    start_date = date(2022,2,10)
    end_date = date(2022,2,18)
    datastorage.get_data_prod_hist_day(start_date, end_date, None, 'EN10', prod_file_path, cfg)

def test_with_only_none_values():
    # test basic functionality
    start_date = date(2022,2,10)
    end_date = date(2022,2,18)
    datastorage.get_data_prod_hist_day(start_date, end_date, None, 'EN11', prod_file_path, cfg)

