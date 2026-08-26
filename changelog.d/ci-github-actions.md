CI moved from GitLab to GitHub Actions. Tests, spellcheck, secret scanning, dependency updates, tagging and releases now all run on GitHub; the GitLab project stays as a break-glass mirror.

The test matrix runs on GitHub-hosted runners across Python 3.11 to 3.14, replacing the dynamically generated GitLab child pipeline.
