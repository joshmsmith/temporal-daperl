# Expense Report Processing Example

A simple, relatable example of using DAPERL to automatically process expense reports.

## Overview

Every company deals with expense report processing. Common issues include:
- Missing receipts
- Expenses over policy limits
- Incorrect categorization
- Duplicate submissions
- Mileage calculations needed

## Files Structure

```
expense_reports/
├── README.md              # This documentation file
├── run_example.py         # Main example runner and demonstration
├── tools.py               # Expense report processing tools
└── data/                  # Data directory
    ├── expense_reports.json  # Sample expense report data
    ├── insights.json      # Generated insights data
    └── metrics.json       # Generated metrics data
```


## Key Features

1. **Detection**: Scans expense reports for policy violations, missing receipts, etc.
2. **Analysis**: Determines root causes (employee error, unclear policy, etc.)
3. **Planning**: Creates actions (request receipt, auto-approve if valid, flag for review)
4. **Execution**: Sends notifications, updates status, calculates amounts
5. **Reporting**: Generates summary of processed reports
6. **Learning**: Identifies patterns (which employees need training, common errors)

## Sample Data

See `data/expense_reports.json` for sample expense reports with various issues:
- Valid reports ready for approval
- Reports missing receipts
- Reports over policy limits
- Reports with mileage that needs calculation
- Duplicate submissions

## Running the Example

```bash
# Start the Temporal server (if connecting locally)
temporal server start-dev

# In another terminal, starting from the project root, create or copy a .env file into the expense_reports folder
cp .env examples/expense_reports/.

# Move to the expense_reports directory
cd examples/expense_reports

# Install the Python dependencies
poetry install

# Start the worker
poetry run python ../../scripts/run_worker.py

# In a third terminal, run the example, either with manual approval (default, send a signal to approve via the Temporal UI)
poetry run python run_example.py

# ...or with auto-approval
poetry run python run_example.py --auto-approve
```

This simple example demonstrates the full DAPERL cycle in a familiar business context!
