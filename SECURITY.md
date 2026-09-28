# Security Policy

## Scope

`castuo-evidence` is a public evidence repository: a scenario runner,
validators, tests, one evidence object and documentation. It runs no service,
holds no credentials and publishes no releases. This policy covers only the
content and workflows of this repository.

## Supported versions

| Version | Supported |
|---|---|
| `main` branch (latest commit) | :white_check_mark: |
| Any other branch or fork | :x: |

## Reporting a vulnerability

Do **not** open a public issue.

Report privately through GitHub: **Security → Report a vulnerability** on
this repository.

Relevant findings include a credential or personal data in the repository or
its history, a workflow that could be abused to write to the repository, or a
way to make a validator accept a tampered evidence object.

This is a single-maintainer project; the times below are targets, not
contractual SLAs:

- Acknowledgement: within 7 days.
- Initial assessment (accepted / declined, with reasoning): within 30 days.

## Evidence integrity

Evidence objects are not edited after publication. Integrity problems
(for example an unverifiable hash or source commit) are recorded as known
defects in the README and resolved by publishing a new, re-anchored evidence
object — never by rewriting the old one.

## Contributions and license

External contributions are not accepted until a contributor licence agreement
(CLA) or contribution policy is defined. No license is currently granted for
this repository (license pending IP review).
