# resverman
Simplified resource version management + storage tools

# dstools

A collection of utility tools for data science projects.

## Installation

To install the package from your local repository, navigate to the root directory of this project in your terminal and run:

```bash
pip install .
```

## Usage

Here are some examples of how to use the core components of `dstools`:

### Resource Management (`dstools.resource_management`)

Manage versioned resources like datasets or models.

```python
# Example usage (conceptual - requires specific implementation details)
from dstools.resource_management import Resource

# Define or load a resource configuration
# config = {'storage': ..., 'versioning': ...} 
# data_resource = Resource(name='my_dataset', config=config)

# Access a specific version
# latest_data = data_resource.get_version('latest') 

# Add a new version
# new_data = ... 
# data_resource.add_version(data=new_data, message='Updated data with new features')

print("Resource management features allow tracking and accessing different versions of assets.")
# Note: Actual usage depends on the specific implementation within resource.py and resource_config.py
```
*(Please refer to the specific classes and methods within `src/dstools/resource_management` for detailed implementation)*

### Reporting (`dstools.reporting`)

Log metrics and information during your processes.

```python
from dstools.reporting import Reporter

# Initialize a reporter (e.g., console reporter)
reporter = Reporter() # Assuming a default or configured reporter

# Report metrics
reporter.report_metric("accuracy", 0.95)
reporter.report_metric("loss", 0.12)

# Report information
reporter.report_info("Training completed.", details={"epochs": 10})

print("\nReporting allows structured logging of metrics and events.")
```
*(See `src/dstools/reporting/reporter.py` for reporter options and configuration)*

### Storage (`dstools.storage`)

Interact with different storage backends using handlers.

```python
# Example usage (conceptual - requires specific handler implementation)
# from dstools.storage import StorageFactory # Assuming a factory pattern
# 
# # Configure and get a storage handler (e.g., local storage)
# local_storage = StorageFactory.get_handler(type='local', config={'base_path': '/data/my_project'})
# 
# # Save data
# data_to_save = {"key": "value"}
# local_storage.save('my_data.json', data_to_save)
# 
# # Load data
# loaded_data = local_storage.load('my_data.json')
# print(f"\nLoaded data from storage: {loaded_data}")

print("\nStorage handlers provide a consistent interface for different backends (e.g., local, S3).")
# Note: Actual usage depends on the handler implementations in src/dstools/storage/handlers/
```
*(Explore `src/dstools/storage/handlers/` for available storage types and their usage)*

### Time Measurement (`dstools.common.time_measure`)

Measure the execution time of code blocks easily.

```python
import time
from dstools.common.time_measure import DurationMeasure, TimeUnit

print("\nUsing DurationMeasure to time an operation:")
with DurationMeasure(action='data processing', unit=TimeUnit.MILLISECONDS) as dm:
    # Simulate some work
    time.sleep(0.15)

print(f"Measured duration: {dm.duration:.2f} {dm._get_unit_suffix(dm.used_unit)}")

# Example with automatic unit fallback
print("\nTiming a very short operation:")
with DurationMeasure(action='quick check', unit=TimeUnit.SECONDS, fallback=True) as dm_short:
    pass # Very fast operation

print(f"Measured duration: {dm_short.duration:.2f} {dm_short._get_unit_suffix(dm_short.used_unit)}")
```
*(See `src/dstools/common/time_measure.py` for more details)*
