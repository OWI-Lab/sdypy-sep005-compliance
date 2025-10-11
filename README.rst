SDyPy SEP005 Compliance
-----------------------

This package serves to assess the compatibility with the SDyPy proposal
for a unified timeseries model, using Pydantic models for robust validation.

Installation
------------
Available from pip: 

.. code-block:: bash

    pip install sdypy-sep005

Using the package
------------------

The main function is the ``assert_sep005`` function that serves to
validate whether a function return is compliant with the current guidelines.

Basic Usage
~~~~~~~~~~~

The primary use case is for unit tests of custom import wrappers:

.. code-block:: python

    from sdypy_sep005.sep005 import assert_sep005
    import numpy as np

    # Your import wrapper
    signals = read_from_path(FILE_PATH)
    
    # Validate compliance
    assert_sep005(signals)

Validating Single Channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from sdypy_sep005.sep005 import assert_sep005_channel
    import numpy as np

    # Valid channel with time vector
    channel = {
        'name': 'acceleration',
        'unit_str': 'm/s^2',
        'data': np.array([1.0, 2.0, 3.0]),
        'time': np.array([0.0, 0.01, 0.02])
    }
    assert_sep005_channel(channel)

    # Valid channel with sampling frequency
    channel_fs = {
        'name': 'velocity',
        'unit_str': 'm/s',
        'data': np.array([1.0, 2.0, 3.0]),
        'fs': 100.0  # 100 Hz
    }
    assert_sep005_channel(channel_fs)

Using Pydantic Models Directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For more advanced usage, you can work directly with the Pydantic models:

.. code-block:: python

    from sdypy_sep005.sep005 import SEP005Channel, SEP005TimeSeriesData
    import numpy as np

    # Create and validate a channel using Pydantic
    channel = SEP005Channel(
        name='temperature',
        unit_str='°C',
        data=np.array([20.5, 21.0, 21.5]),
        fs=1.0,
        start_timestamp='2023-08-23T12:00:00'  # ISO8601 format
    )

    # Access validated data
    print(f"Channel name: {channel.name}")
    print(f"Data points: {len(channel.data)}")

    # Validate multiple channels
    channels_data = [
        {
            'name': 'ch1',
            'unit_str': 'm',
            'data': np.array([1, 2, 3]),
            'fs': 100.0
        },
        {
            'name': 'ch2',
            'unit_str': 'N',
            'data': np.array([4, 5, 6]),
            'time': np.array([0.0, 0.01, 0.02])
        }
    ]
    timeseries = SEP005TimeSeriesData.from_input(channels_data)

Validation Rules
~~~~~~~~~~~~~~~~

The SEP005 standard requires:

**Compulsory Fields:**

- ``data``: NumPy array containing the measurement data
- ``name``: String identifying the channel
- ``unit_str``: String describing the unit of measurement
- Either ``time`` (NumPy array) or ``fs`` (sampling frequency) must be provided

**Prohibited Fields:**

- ``timestamp``: Use ``start_timestamp``, ``end_timestamp``, etc. instead

**Additional Validation:**

- If ``time`` is provided, it must have the same length as ``data``
- Any field containing 'timestamp' in its name must be in ISO8601 format
- Field names are case-sensitive (e.g., use ``unit_str``, not ``Unit_Str``)

Error Handling
~~~~~~~~~~~~~~

The package uses Pydantic's validation, which provides detailed error messages:

.. code-block:: python

    from pydantic import ValidationError
    from sdypy_sep005.sep005 import assert_sep005_channel
    import numpy as np

    try:
        # Missing required 'name' field
        invalid_channel = {
            'unit_str': 'm',
            'data': np.array([1, 2, 3]),
            'fs': 100.0
        }
        assert_sep005_channel(invalid_channel)
    except ValidationError as e:
        print(f"Validation failed: {e}")

Backward Compatibility
~~~~~~~~~~~~~~~~~~~~~~

Legacy validation functions are still available for backward compatibility:

.. code-block:: python

    from sdypy_sep005.sep005 import (
        check_compulsory_fields,
        check_prohibited_fields,
        check_timestamp_iso8601
    )

    # These functions work as before
    keys = ['data', 'name', 'unit_str', 'fs']
    check_compulsory_fields(keys)
    check_prohibited_fields(keys)
