Code documentation
==================

SEP005 Validation Module
-------------------------
.. automodule:: sdypy_sep005.sep005
    :members:
    :undoc-members:
    :show-inheritance:

Pydantic Models
~~~~~~~~~~~~~~~

The package uses Pydantic models for robust validation:

- **SEP005Channel**: Validates individual channel data
- **SEP005TimeSeriesData**: Validates single or multiple channels

Validation Functions
~~~~~~~~~~~~~~~~~~~~

Main validation functions:

- **assert_sep005**: Validates timeseries data (dict or list of dicts)
- **assert_sep005_channel**: Validates a single channel

Legacy Functions
~~~~~~~~~~~~~~~~

For backward compatibility:

- **check_compulsory_fields**: Check required fields are present
- **check_prohibited_fields**: Check prohibited fields are not present
- **check_timestamp_iso8601**: Validate timestamp format