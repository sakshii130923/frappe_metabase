# Frappe Metabase

Embed Metabase dashboards and questions inside Frappe / ERPNext with role-based access control and dynamic parameter mapping.

![Frappe v15+](https://img.shields.io/badge/Frappe-v15%2B-blue)
![Metabase v0.46+](https://img.shields.io/badge/Metabase-v0.46%2B-blueviolet)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

## Features

- **Metabase Settings** — single config page for your Metabase URL and embedding secret key, with a one-click connection test
- **Dashboard & Question Doctypes** — register each embed as a Frappe document with its own access control and parameters
- **Role-Based Access** — restrict which Frappe roles can see which dashboards
- **Dynamic Parameter Mapping** — lock Metabase filter params to static values, User fields, or custom Frappe methods
- **Gallery Page** — a single page listing all dashboards/questions the current user can access
- **Reusable JS Helper** — call `frappe.metabase.embed()` from any page, form, or workspace
- **Dark Mode** — auto-apply Metabase night theme
- **Signed JWT Tokens** — short-lived (10 min default), generated server-side, no Metabase login needed for end users

## Installation

```bash
cd ~/frappe-bench

# Get the app
bench get-app https://github.com/your-org/frappe_metabase.git

# Install on your site
bench --site your-site.local install-app frappe_metabase

# Build assets
bench build --app frappe_metabase
```

## Setup

### 1. Enable Embedding in Metabase

1. Go to **Metabase Admin → Settings → Embedding**
2. Enable embedding and copy the **Secret Key**
3. Open each dashboard/question you want to embed → **Share → Embed** → **Publish**

### 2. Configure Frappe

1. Open **Metabase Settings** (search in the Frappe awesomebar)
2. Enter your Metabase Server URL and Secret Key
3. Click **Test Connection** to verify

### 3. Register Dashboards

1. Create a new **Metabase Dashboard** document
2. Enter the title and Metabase Dashboard ID (from the URL, e.g. `/dashboard/3` → `3`)
3. Optionally set allowed roles and locked parameters
4. Click **Preview Dashboard** to verify it works
5. Save

### 4. Access

- **Gallery:** Go to `/app/metabase-gallery` to see all dashboards you have access to
- **Direct link:** `/app/metabase-gallery?dashboard=Sales+Overview`
- **From JS:** Use `frappe.metabase.embed()` anywhere (see below)

## Usage

### Embed in a Custom Page

```javascript
frappe.metabase.embed({
    container: ".my-container",
    doctype: "Metabase Dashboard",
    name: "Sales Overview",
    height: 900, // optional
});
```

### Dynamic Parameters

In the **Locked Parameters** table on a dashboard, you can map Metabase filter params to Frappe data:

| Source Type | Example | Description |
|---|---|---|
| **Static** | `param: company`, value: `My Company` | Always passes a fixed value |
| **User Field** | `param: company`, field: `company` | Reads from the current user's User doc |
| **User Field** | `param: warehouse`, field: `perm:Warehouse` | Reads from UserPermission (all allowed warehouses) |
| **Frappe Method** | `param: branches`, method: `myapp.utils.get_user_branches` | Calls a custom method |

## Requirements

- Frappe v15 or v16
- Metabase v0.46+ with embedding enabled
- Python 3.10+

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.
