# Security Policy

## Public verification repository

This repository is intentionally public and must contain only public mathematical sources, verification infrastructure, workflow evidence and public documentation.

## Reporting a security issue

Do **not** open a public issue containing:

- access tokens, passwords or credentials;
- private personal or customer data;
- unpublished CMIS, CBI, TBC, Gmail, investor or commercial material;
- a private filesystem path that exposes sensitive project information; or
- a reproducible exploit that could endanger another system.

Use GitHub's private **Report a vulnerability** function under the repository's **Security** tab when available. Describe the affected file or workflow, the impact, the minimum reproduction steps and any immediate containment action.

## Accidental secret exposure

If a credential is committed or printed in a workflow log:

1. revoke or rotate it immediately;
2. stop any affected workflow;
3. preserve a private incident record;
4. remove the public value from the current repository state; and
5. treat the value as compromised even after deletion, because Git history and caches may retain it.

## Supported version

The living `main` branch and the latest tagged release receive security attention. Earlier tags remain immutable evidence snapshots and may receive a later advisory rather than a rewritten tag.
