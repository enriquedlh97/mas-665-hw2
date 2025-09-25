### Observed hardcoded Anthropic model

- Upstream reference: `nanda_adapter/core/agent_bridge.py` at commit `89e8558`
  https://github.com/projnanda/adapter/blob/89e8558158b88f5ef1d08a7b4de08e05f967be14/nanda_adapter/core/agent_bridge.py#L173
- The model is hardcoded to "claude-3-5-sonnet-20241022", which returned a 404 from Anthropic in my environment.
- Workaround: switching to "claude-3-haiku-20240307" resolved the issue.
- Suggestion: make the model configurable via environment variable or settings to avoid breakage when models are unavailable or renamed.

### NANDA Registry availability issues

- The registry site intermittently failed with: "Error checking user. Please try again." across multiple browsers.
- The subdomain `chat.nanda-registry.com` was not reachable on port `6900` during testing; this likely explains registration failures and sign-in issues observed.
- Action: if registration fails, retry later and/or confirm registry service status. Capture the enrollment link from logs for later use.

### Enrollment link captured

- Enrollment URL: https://chat.nanda-registry.com/landing.html?agentId=agents997004
