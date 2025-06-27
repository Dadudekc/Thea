# CI Pipeline Summary – Beta Readiness

The full test suite could not be executed due to missing dependencies. The `undetected_chromedriver` package was unavailable in the environment which resulted in an internal error when running `pytest`.

Only `tests/test_advanced_search.py` executed successfully.

```
$ pytest tests/test_advanced_search.py -q
1 passed in 0.12s
```

All other tests were skipped.
