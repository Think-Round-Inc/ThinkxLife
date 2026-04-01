# Security Policy

ThinkLife is committed to the security and privacy of its users.  This document describes our process for reporting and handling vulnerabilities in the ThinkLife codebase.

---

## Supported Versions

| Branch / Version | Supported?      | Notes                          |
|------------------|-----------------|--------------------------------|
| `main`           | Yes (latest)    | All new fixes land here first  |
| `Collborator`          | Yes             | Mirrors `main` via CI/CD       |

We aim to provide security fixes for all supported branches.  Please report any issues you find against the branch you’re using.

---

## Reporting a Vulnerability

If you discover a security issue, please use **one** of the methods below:

### 1. GitHub Security Advisory (recommended)
1. Go to the **Security → Advisories** tab of the Think-Round-Inc/ThinkxLife repository.
2. Click **“New draft”** to open a private advisory.
3. Provide as much detail as possible (steps to reproduce, impact, suggested fix).

GitHub will keep your report private until a fix is ready for public disclosure.

### 2. Email
Send an encrypted or plain-text email to: info@thinkround.org


Subject line: `Security vulnerability in ThinkLife`

Include:
- **Summary** of the issue
- **Affected versions** / branches
- **Steps to reproduce** and/or a proof-of-concept
- **Impact** assessment
- **Suggested remediation** (if you have one)

---

## Response and Disclosure Timeline

| Action                      | Timeline         |
|-----------------------------|------------------|
| Acknowledge receipt        | ASAP  |
| Initial triage & classification | ASAP |
| Fix or mitigation released | ASAP |
| Public disclosure          | After patch release (unless you request otherwise) |

We will keep you updated at each stage.  Thank you for helping us keep ThinkLife secure!

---

## Maintainers & Contacts

- **Heidi Hardin** (Founder, Think Round, Inc)
- **Generative AI Engineers**


For general support or non-security issues, please open a regular issue in the repo.

---

## Secure Development

- All pull requests are scanned with automated security linters (e.g., Snyk, Dependabot)
- Dependencies are kept up-to-date and reviewed before merging
- Secrets and keys must never be committed—use GitHub Secrets for CI workflows

---

## Acknowledgments

We appreciate responsible disclosure.  Reporters of confirmed vulnerabilities may be acknowledged by name in our release notes or SECURITY.md (with your permission).

---

## References

- GitHub Security Advisories: https://docs.github.com/en/code-security/security-advisories
- OWASP Responsible Disclosure: https://owasp.org/www-project-responsible-disclosure/
