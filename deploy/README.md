# Streamlit Deployment Profiles

The repository default is intentionally safe for a developer workstation:

```toml
[server]
address = "127.0.0.1"
enableCORS = true
enableXsrfProtection = true
```

## Local Windows development

Run normally from the repository root:

```powershell
streamlit run dashboard.py
```

Expected startup output should contain only a local `127.0.0.1` URL.

## Hosted or container deployment

A container or managed hosting platform usually needs a broad bind *inside the
container*. Override the committed local address with the standard Streamlit
environment variable:

```text
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Keep:

```text
STREAMLIT_SERVER_ENABLE_CORS=true
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

External exposure should then be controlled by the hosting platform or reverse
proxy. For real CRM data, that external layer must also provide proper
authentication and authorization.

This separation allows the same repository to remain loopback-only by default on
a workstation without hard-coding an unsafe bind for local development.
