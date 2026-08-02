Feature: Signal clustering

  Background:
    Given the user belongs to tenant "acme"
    And the Signal Clustering feature flag is enabled for tenant "acme"

  Scenario: Similar support signals produce one candidate cluster
    Given tenant "acme" has these feedback signals:
      | source  | account | text |
      | support | Alpha   | Exported release notes miss rollback details |
      | support | Beta    | We need rollback guidance in release notes |
      | sales   | Gamma   | Buyers ask how rollback is documented |
    When the product owner asks for signal clustering
    Then the system proposes a candidate cluster named "Rollback details in release notes"
    And the cluster contains all three signals as evidence
    And the cluster confidence is at least "medium"
    And no product spec is generated yet

  Scenario: Conflicting signals stay visible before validation
    Given tenant "acme" has signals about release notes
    And one signal asks for shorter release notes
    And another signal asks for more detailed rollback guidance
    When the product owner reviews the candidate cluster
    Then the system shows a conflict named "detail level"
    And the system suggests "split cluster" as an available decision

  Scenario: Low confidence blocks automatic spec generation
    Given tenant "acme" has a candidate cluster with confidence "low"
    When the product owner opens the cluster
    Then the system marks the cluster as "needs review"
    And the "Generate spec" action is disabled
    And the system explains the missing evidence

  Scenario: Accepted cluster generates a spec draft with evidence
    Given tenant "acme" has a candidate cluster named "Rollback details in release notes"
    And the product owner accepts the cluster
    When the product owner generates a spec draft
    Then the draft includes the problem summary
    And the draft includes the source evidence
    And the draft includes acceptance criteria
    And the draft links back to the validation decision

  Scenario: Tenant isolation protects signal data
    Given tenant "acme" has a candidate cluster
    And tenant "otherco" has a different product owner
    When the "otherco" product owner requests the "acme" cluster
    Then the system denies access
    And the event is audit logged
