# Security and Deployment Scope

This repository is a BI/decision-support **demo built with synthetic CRM data**.

## Public demo

The public Streamlit demo intentionally contains no application-level login because
the included data is synthetic and non-confidential. This does **not** mean the
same deployment model is appropriate for real CRM data.

## Real CRM data

Do not add a simple password check inside `dashboard.py` and treat it as production
authentication. A real-data deployment should sit behind an authentication and
authorization layer that provides proper identity, session, token, and access
control management, such as an organization SSO gateway, authenticated reverse
proxy, or managed platform access-control layer.

## Streamlit protections

The committed Streamlit configuration keeps CORS and XSRF protections enabled.

Local workstation development binds to:

```text
127.0.0.1:8501
```

so the dashboard is not exposed to the LAN.

Hosted/container deployments often need to listen on all container interfaces.
In those environments, override only the address at deployment time:

```text
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Do **not** disable CORS or XSRF to make forwarding work. The container, forwarding
layer, reverse proxy, and authentication layer are responsible for external
exposure and access control.

## Secrets

`.streamlit/config.toml` is committed.

`.streamlit/secrets.toml` must never be committed and is ignored by Git.

## Before deploying real data

Verify all of the following:

- the deployment has a real authentication/authorization layer;
- the forwarded/public port is intentionally scoped;
- CORS remains enabled;
- XSRF protection remains enabled;
- CSV or database-derived text is escaped before custom HTML rendering;
- secrets are supplied by the hosting platform, not committed files;
- error responses do not expose raw tracebacks or filesystem paths.
