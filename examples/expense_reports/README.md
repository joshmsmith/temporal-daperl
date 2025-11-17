# Expense Report Processing Example

A simple, relatable example of using DAPERL to automatically process expense reports.

## The Problem

Every company deals with expense report processing. Common issues include:
- Missing receipts
- Expenses over policy limits
- Incorrect categorization
- Duplicate submissions
- Mileage calculations needed

## How DAPERL Solves It

1. **Detection**: Scans expense reports for policy violations, missing receipts, etc.
2. **Analysis**: Determines root causes (employee error, unclear policy, etc.)
3. **Planning**: Creates actions (request receipt, auto-approve if valid, flag for review)
4. **Execution**: Sends notifications, updates status, calculates amounts
5. **Reporting**: Generates summary of processed reports
6. **Learning**: Identifies patterns (which employees need training, common errors)

## Running the Example

```bash
# Start from project root
cd examples/expense_reports

# Run with manual approval (default)
poetry run python run_example.py

# Run with auto-approval for demo purposes
poetry run python run_example.py --auto-approve
```

### Command Line Options

- `--auto-approve`: Auto-approve actions without human intervention (default: False)
- `--help`: Show help message and available options
```

## Sample Data

See `data/expense_reports.json` for sample expense reports with various issues:
- Valid reports ready for approval
- Reports missing receipts
- Reports over policy limits
- Reports with mileage that needs calculation
- Duplicate submissions

## Expected Output

The system will:
1. Detect 4-5 problems in the expense reports
2. Analyze root causes (missing documentation, policy violations)
3. Create a plan to fix issues (request receipts, auto-calculate mileage, flag for review)
4. Execute the plan (simulated - in production would send emails, update database)
5. Generate a report of what was processed
6. Learn patterns for future processing

This simple example demonstrates the full DAPERL cycle in a familiar business context!
