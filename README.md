# TMetric filler

This script exists only to fill TMetric timesheet from dev perspective. It
inserts up to 8 hours for each day except Saturday and Sunday since
__the next workday after last entry__ to __today__. If you have entry today, it
won't put anything.

## Config

Create config.py file and put proper values inside:

```python
bearer_auth_key = 'API token from https://app.tmetric.com/#/profile'
my_project_id = 'Name of the project'
```

## Install

```sh
pip3 install -r requirements.txt
```

## Launch

```sh
./main.py
```
