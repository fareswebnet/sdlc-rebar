Feature: Report export

  @FR-001
  Scenario: Export a report as CSV
    Given a report with 3 rows
    When the user exports it
    Then a CSV with 3 rows is downloaded

  @FR-002
  Scenario: Export is audited
    When the user exports a report
    Then an audit entry is recorded

  @NFR-001
  Scenario: Large export is fast
    Given a report with 10000 rows
    When the user exports it
    Then the export finishes in under 5 seconds
