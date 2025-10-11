import numpy as np
from datetime import datetime
from typing import Union, List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# Constants for backward compatibility
COMPULSORY_FIELDS = ['data', 'name', 'unit_str']
PROHIBITED_FIELDS = ['timestamp']


class SEP005Channel(BaseModel):
    """
    Pydantic model representing a SEP005-compliant channel.
    
    Validates compliance with the SEP005 guidelines as specified in
    https://github.com/sdypy/sdypy/blob/main/docs/seps/sep-0005.rst
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    
    # Compulsory fields
    data: np.ndarray = Field(..., description="Data array for the channel")
    name: str = Field(..., description="Channel name")
    unit_str: str = Field(..., description="Unit string for the channel")
    
    # Optional time information (at least one must be provided)
    time: Optional[np.ndarray] = Field(None, description="Time vector")
    fs: Optional[float] = Field(None, description="Sampling frequency")
    
    @field_validator('data')
    @classmethod
    def validate_data_type(cls, v):
        """Validate that data is a numpy array"""
        if not isinstance(v, np.ndarray):
            raise TypeError(f"Invalid datatype {type(v)}, should be np.array")
        return v
    
    @field_validator('time')
    @classmethod
    def validate_time_type(cls, v):
        """Validate that time is a numpy array if provided"""
        if v is not None and not isinstance(v, np.ndarray):
            raise TypeError(f"Invalid datatype {type(v)}, should be np.array")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def check_prohibited_fields(cls, data: Any) -> Any:
        """Check that prohibited fields are not present and validate field names"""
        if not isinstance(data, dict):
            raise TypeError(f'Invalid datatype {type(data)}, should be dict')
        
        keys = list(data.keys())
        
        # Check for case errors in compulsory fields
        for key in keys:
            if key.lower() in [c_key.lower() for c_key in COMPULSORY_FIELDS] and (key not in COMPULSORY_FIELDS):
                for c_key in COMPULSORY_FIELDS:
                    if key.lower() == c_key.lower():
                        raise ValueError(f"'{key}' is an invalid keyword, please use '{c_key}' instead.")
        
        # Check for prohibited fields
        for key in keys:
            if key.lower() in [p_key.lower() for p_key in PROHIBITED_FIELDS]:
                raise ValueError(f"'{key}' is a Prohibited keyword, do not use it.")
        
        return data
    
    @model_validator(mode='after')
    def validate_time_information(self):
        """Validate that either time or fs is provided"""
        if self.time is None and self.fs is None:
            raise ValueError("Missing information to replicate time")
        return self
    
    @model_validator(mode='after')
    def validate_time_data_length(self):
        """Validate that time and data have the same length"""
        if self.time is not None:
            if len(self.time) != len(self.data):
                raise ValueError(
                    f"Length of the time vector and data vector do not match :"
                    f" {len(self.time)} vs. {len(self.data)}"
                )
        return self
    
    @model_validator(mode='after')
    def validate_timestamps_iso8601(self):
        """Validate that any timestamp fields are in ISO8601 format"""
        for key, value in self.model_dump(exclude_unset=True).items():
            if 'timestamp' in key and isinstance(value, str):
                try:
                    datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    raise TypeError(f"Timestamp '{key}':{value} is not according to ISO8601")
        return self


class SEP005TimeSeriesData(BaseModel):
    """
    Pydantic model for validating SEP005 timeseries data (single channel or list of channels).
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    channels: List[SEP005Channel]
    
    @classmethod
    def from_input(cls, timeseries: Union[Dict, List[Dict]]) -> 'SEP005TimeSeriesData':
        """Create SEP005TimeSeriesData from dict or list of dicts"""
        if isinstance(timeseries, dict):
            channels = [timeseries]
        elif isinstance(timeseries, list):
            channels = timeseries
        else:
            raise TypeError(f'Invalid datatype {type(timeseries)}, should be list or dict')
        
        return cls(channels=channels)


def assert_sep005(timeseries: Union[Dict, List[Dict]]) -> None:
    """
    Assert the compliance with the SEP005 guidelines as specified in
    https://github.com/sdypy/sdypy/blob/main/docs/seps/sep-0005.rst
    
    Args:
        timeseries: A dictionary representing a single channel or a list of dictionaries
                    representing multiple channels.
    
    Raises:
        TypeError: If the input type is invalid or field types are incorrect
        ValueError: If required fields are missing or validation fails
    """
    # Validate using Pydantic model
    SEP005TimeSeriesData.from_input(timeseries)


def assert_sep005_channel(channel: dict) -> None:
    """
    Assert the compliance of an individual channel
    
    Args:
        channel: Dictionary representing a single channel
        
    Raises:
        TypeError: If the channel type is invalid or field types are incorrect
        ValueError: If required fields are missing or validation fails
    """
    # Validate using Pydantic model
    SEP005Channel(**channel)


# Legacy functions for backward compatibility
def check_compulsory_fields(keywords: list) -> None:
    """
    Check that all the compulsory fields are present
    
    Note: This function is maintained for backward compatibility.
    Consider using assert_sep005_channel() with Pydantic validation instead.
    """
    for c_key in COMPULSORY_FIELDS:
        if c_key not in keywords:
            raise ValueError(f"Missing compulsory keyword '{c_key}'")
    
    if 'time' not in keywords and 'fs' not in keywords:
        raise ValueError("Missing information to replicate time")


def check_prohibited_fields(keywords: list) -> None:
    """
    Checks that none of the prohibited fields are included in the channels keywords
    
    - Check errors in case in the compulsory fields
    - Check if none of the fields are in the forbidden field list
    
    Note: This function is maintained for backward compatibility.
    Consider using assert_sep005_channel() with Pydantic validation instead.
    """
    for key in keywords:
        if key.lower() in [c_key.lower() for c_key in COMPULSORY_FIELDS] and (key not in COMPULSORY_FIELDS):
            for c_key in COMPULSORY_FIELDS:
                if key.lower() == c_key.lower():
                    raise ValueError(f"'{key}' is an invalid keyword, please use '{c_key}' instead.")
    
    for key in keywords:
        if key.lower() in [p_key.lower() for p_key in PROHIBITED_FIELDS]:
            raise ValueError(f"'{key}' is a Prohibited keyword, do not use it.")


def check_timestamp_iso8601(channel: dict) -> None:
    """
    Check that any timestamp provided is in ISO8601
    
    Note: This function is maintained for backward compatibility.
    Consider using assert_sep005_channel() with Pydantic validation instead.
    """
    keys = list(channel.keys())
    
    for key in keys:
        if 'timestamp' in key:
            dt_str = channel[key]
            try:
                datetime.fromisoformat(dt_str)
            except (ValueError, TypeError):
                raise TypeError(f"Timestamp '{key}':{dt_str} is not according to ISO8601")
