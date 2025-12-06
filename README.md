# PR_PY

**A lightweight Python utility for structured console reporting.**

Print structured logs (INFO, WARN, FAIL, ERROR, FATAL) and get an automatic summary when execution finishes.
Perfect for long-running scripts, build pipelines, data generation processes, and automation where you want clear, readable terminal output.

----------------------------------------

## Getting Started
`pip install pr_py`

### Implementation
```py
from pr_py import INIT_REPORTS, PR_INFO, PR_WARN, PR_FAIL

INIT_REPORTS() # enables automatic exit summary

PR("Starting", ln=True)
PR_INFO("Processing assets...", pre="INFO HEADER")
PR_WARN("Value missing, using fallback")
PR_FAIL("Something went wrong")

# When the script exits, a summary report will print automatically.
```

### License

MIT License — free for personal and commercial use.