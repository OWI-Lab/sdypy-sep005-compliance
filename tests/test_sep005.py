import pytest
import sdypy_sep005

import numpy as np

from datetime import datetime, timezone
from hypothesis import given, strategies as st, assume
from pydantic import ValidationError

# Pytest will discover and run all test functions named `test_*` or `*_test`.

def test_version():
    """ check sdypy_template_project exposes a version attribute """
    assert hasattr(sdypy_sep005, "__version__")
    assert isinstance(sdypy_sep005.__version__, str)


def test_prohibited_keywords():
    from sdypy_sep005.sep005 import check_prohibited_fields

    with pytest.raises(ValueError, match="'timestamp' is a Prohibited keyword"):
        check_prohibited_fields(['timestamp'])

    for bad_key in ['Unit_Str']:
        with pytest.raises(ValueError, match=f"'{bad_key}' is an invalid keyword"):
            check_prohibited_fields([bad_key])

def test_compulsory_keywords():
    import copy
    import random

    from sdypy_sep005.sep005 import check_compulsory_fields
    from sdypy_sep005.sep005 import COMPULSORY_FIELDS

    # Shouldn't pass as time info is missing
    with pytest.raises(ValueError):
        check_compulsory_fields(COMPULSORY_FIELDS)

    comp_list = copy.copy(COMPULSORY_FIELDS)
    comp_list.append('fs')
    check_compulsory_fields(comp_list) # Should pass

    # Remove random element, shouldn't pass
    random_element = random.choice(COMPULSORY_FIELDS)
    comp_list.remove(random_element)
    with pytest.raises(ValueError):
        check_compulsory_fields(comp_list)

def test_assert_sep005():
    from sdypy_sep005.sep005 import assert_sep005

    dummy_channels = [
        {
            'name' : 'test',
            'unit_str': 'm',
            'data': np.array([1,2,3]),
            'time': np.array([1,2,3])
        }
    ]

    assert_sep005(dummy_channels)

    #
    dummy_channels.append(
        {
            'name': 'test',
            'unit_str': 'm',
            'data': np.array([1, 2, 3]),
            'time': np.array([1, 3])
        }
    )

    with pytest.raises(ValueError, match= 'Length of the time vector and data vector do not match'):
        assert_sep005(dummy_channels)

    # Type errors
    with pytest.raises(TypeError):
        assert_sep005('Not SEP005 compliant')   # string

    with pytest.raises(TypeError):
        assert_sep005([[]]) # Channel should be dict, not list

def test_timestamps():
    from sdypy_sep005.sep005 import check_timestamp_iso8601

    check_timestamp_iso8601(
        {'start_timestamp': str(datetime.now(timezone.utc))}
    )
    with pytest.raises(TypeError, match="end_timestamp"):
        check_timestamp_iso8601(
            {
                'start_timestamp': str(datetime.now(timezone.utc)),
                'end_timestamp': '2023/08/23 1200',
             }
        )


# Pydantic-specific tests
def test_pydantic_channel_model():
    """Test that SEP005Channel Pydantic model works correctly"""
    from sdypy_sep005.sep005 import SEP005Channel
    
    # Valid channel with time
    channel = SEP005Channel(
        data=np.array([1.0, 2.0, 3.0]),
        name="test_channel",
        unit_str="m/s",
        time=np.array([0.0, 1.0, 2.0])
    )
    assert channel.name == "test_channel"
    assert len(channel.data) == 3
    
    # Valid channel with fs
    channel_fs = SEP005Channel(
        data=np.array([1.0, 2.0, 3.0]),
        name="test_channel",
        unit_str="m/s",
        fs=100.0
    )
    assert channel_fs.fs == 100.0
    
    # Invalid: missing time/fs
    with pytest.raises(ValidationError, match="Missing information to replicate time"):
        SEP005Channel(
            data=np.array([1.0, 2.0, 3.0]),
            name="test_channel",
            unit_str="m/s"
        )
    
    # Invalid: time/data length mismatch
    with pytest.raises(ValidationError, match="Length of the time vector and data vector do not match"):
        SEP005Channel(
            data=np.array([1.0, 2.0, 3.0]),
            name="test_channel",
            unit_str="m/s",
            time=np.array([0.0, 1.0])
        )


def test_pydantic_timeseries_model():
    """Test that SEP005TimeSeriesData Pydantic model works correctly"""
    from sdypy_sep005.sep005 import SEP005TimeSeriesData
    
    # Valid single channel as dict
    single_channel = {
        'data': np.array([1.0, 2.0, 3.0]),
        'name': 'test',
        'unit_str': 'm',
        'time': np.array([0.0, 1.0, 2.0])
    }
    ts_data = SEP005TimeSeriesData.from_input(single_channel)
    assert len(ts_data.channels) == 1
    
    # Valid multiple channels as list
    multi_channels = [
        {
            'data': np.array([1.0, 2.0, 3.0]),
            'name': 'test1',
            'unit_str': 'm',
            'fs': 100.0
        },
        {
            'data': np.array([4.0, 5.0, 6.0]),
            'name': 'test2',
            'unit_str': 'N',
            'time': np.array([0.0, 1.0, 2.0])
        }
    ]
    ts_data_multi = SEP005TimeSeriesData.from_input(multi_channels)
    assert len(ts_data_multi.channels) == 2


def test_pydantic_prohibited_fields():
    """Test that prohibited fields raise appropriate errors"""
    from sdypy_sep005.sep005 import SEP005Channel
    
    # Test prohibited 'timestamp' field
    with pytest.raises(ValidationError, match="'timestamp' is a Prohibited keyword"):
        SEP005Channel(
            data=np.array([1.0, 2.0, 3.0]),
            name="test",
            unit_str="m",
            time=np.array([0.0, 1.0, 2.0]),
            timestamp="2023-01-01T00:00:00"
        )


def test_pydantic_case_sensitive_fields():
    """Test that field names are case-sensitive"""
    from sdypy_sep005.sep005 import assert_sep005_channel
    
    # Wrong case should fail
    with pytest.raises(ValidationError, match="'Unit_Str' is an invalid keyword"):
        assert_sep005_channel({
            'data': np.array([1.0, 2.0, 3.0]),
            'name': 'test',
            'Unit_Str': 'm',  # Wrong case
            'fs': 100.0
        })


def test_pydantic_timestamp_validation():
    """Test ISO8601 timestamp validation"""
    from sdypy_sep005.sep005 import SEP005Channel
    
    # Valid ISO8601 timestamp
    channel_valid = SEP005Channel(
        data=np.array([1.0, 2.0, 3.0]),
        name="test",
        unit_str="m",
        fs=100.0,
        start_timestamp="2023-08-23T12:00:00"
    )
    assert channel_valid.model_extra['start_timestamp'] == "2023-08-23T12:00:00"
    
    # Invalid timestamp format - ValidationError wraps the TypeError
    with pytest.raises((ValidationError, TypeError), match="not according to ISO8601"):
        SEP005Channel(
            data=np.array([1.0, 2.0, 3.0]),
            name="test",
            unit_str="m",
            fs=100.0,
            end_timestamp="2023/08/23 1200"
        )


# Property-based tests using Hypothesis
@given(
    data_size=st.integers(min_value=1, max_value=100),
    name=st.text(min_size=1, max_size=20),
    unit=st.text(min_size=1, max_size=10),
    fs=st.floats(min_value=0.1, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
def test_hypothesis_valid_channel_with_fs(data_size, name, unit, fs):
    """Property-based test: any valid channel with fs should pass validation"""
    from sdypy_sep005.sep005 import assert_sep005_channel
    
    channel = {
        'data': np.random.randn(data_size),
        'name': name,
        'unit_str': unit,
        'fs': fs
    }
    
    # Should not raise any exception
    assert_sep005_channel(channel)


@given(
    data_size=st.integers(min_value=1, max_value=100),
    name=st.text(min_size=1, max_size=20),
    unit=st.text(min_size=1, max_size=10)
)
def test_hypothesis_valid_channel_with_time(data_size, name, unit):
    """Property-based test: any valid channel with matching time should pass validation"""
    from sdypy_sep005.sep005 import assert_sep005_channel
    
    channel = {
        'data': np.random.randn(data_size),
        'name': name,
        'unit_str': unit,
        'time': np.arange(data_size, dtype=float)
    }
    
    # Should not raise any exception
    assert_sep005_channel(channel)


@given(
    data_size=st.integers(min_value=1, max_value=100),
    time_size=st.integers(min_value=1, max_value=100),
    name=st.text(min_size=1, max_size=20),
    unit=st.text(min_size=1, max_size=10)
)
def test_hypothesis_mismatched_time_data_length(data_size, time_size, name, unit):
    """Property-based test: mismatched time and data lengths should fail"""
    from sdypy_sep005.sep005 import assert_sep005_channel
    
    # Only test when sizes are different
    assume(data_size != time_size)
    
    channel = {
        'data': np.random.randn(data_size),
        'name': name,
        'unit_str': unit,
        'time': np.arange(time_size, dtype=float)
    }
    
    # Should raise ValueError
    with pytest.raises((ValidationError, ValueError)):
        assert_sep005_channel(channel)


@given(
    num_channels=st.integers(min_value=1, max_value=10),
    data_size=st.integers(min_value=1, max_value=50)
)
def test_hypothesis_multiple_channels(num_channels, data_size):
    """Property-based test: multiple valid channels should pass validation"""
    from sdypy_sep005.sep005 import assert_sep005
    
    channels = []
    for i in range(num_channels):
        channels.append({
            'data': np.random.randn(data_size),
            'name': f'channel_{i}',
            'unit_str': 'm',
            'fs': 100.0
        })
    
    # Should not raise any exception
    assert_sep005(channels)


@given(
    data_size=st.integers(min_value=1, max_value=100),
    name=st.text(min_size=1, max_size=20),
    unit=st.text(min_size=1, max_size=10)
)
def test_hypothesis_missing_time_info(data_size, name, unit):
    """Property-based test: missing both time and fs should fail"""
    from sdypy_sep005.sep005 import assert_sep005_channel
    
    channel = {
        'data': np.random.randn(data_size),
        'name': name,
        'unit_str': unit
        # Missing both 'time' and 'fs'
    }
    
    # Should raise ValidationError
    with pytest.raises((ValidationError, ValueError)):
        assert_sep005_channel(channel)