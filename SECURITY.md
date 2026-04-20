# Security

## Scope

tailtest-cursor is a Cursor plugin that hooks into Cursor's agent lifecycle. The plugin:

- Reads files and manifests in the user's project to detect test runners
- Reads and writes `.cursor/hooks/state/tailtest.json` (session state)
- Reads and writes `.tailtest/` (config, reports)
- Does not make network requests
- Does not collect or transmit data
- Does not execute arbitrary code -- it instructs the Cursor agent to run test commands that the user's own project defines

## Reporting vulnerabilities

To report a security vulnerability, email security@avansaber.com.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

We will respond within 72 hours and aim to release a fix within 14 days of confirmation.

## Supported versions

Only the latest release receives security fixes.
