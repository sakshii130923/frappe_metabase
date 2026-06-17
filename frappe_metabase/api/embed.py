import frappe

from frappe_metabase.utils.params import resolve_params
from frappe_metabase.utils.token import build_embed_url, generate_embed_token


@frappe.whitelist()
def get_embed_url(doctype: str, name: str) -> dict:
    """
    Generate a signed embed URL for a Metabase Dashboard or Question.

    Validates role-based access, resolves locked parameters, generates
    a JWT token, and returns the full iframe URL.

    Args:
        doctype: "Metabase Dashboard" or "Metabase Question"
        name: document name

    Returns:
        dict: { url, title, height, resource_type }
    """
    if doctype not in ("Metabase Dashboard", "Metabase Question"):
        frappe.throw(
            "Invalid doctype. Must be Metabase Dashboard or Metabase Question."
        )

    doc = frappe.get_doc(doctype, name)

    # Check if embed is active
    if not doc.is_active:
        frappe.throw(f"{doc.title} is currently disabled.", title="Embed Disabled")

    # Check role-based access
    _check_role_access(doc)

    # Resolve locked parameters
    params = resolve_params(doc.locked_params) if doc.locked_params else {}

    # Determine resource type and ID
    if doctype == "Metabase Dashboard":
        resource_type = "dashboard"
        resource_id = doc.dashboard_id
    else:
        resource_type = "question"
        resource_id = doc.question_id

    # Check dark mode setting
    settings = frappe.get_single("Metabase Settings")
    dark_mode = bool(settings.enable_dark_mode)

    # Generate token
    token = generate_embed_token(
        resource_type=resource_type,
        resource_id=resource_id,
        params=params,
        expiry_min=doc.expiry_override_min or None,
    )

    # Build full URL
    url = build_embed_url(
        resource_type=resource_type,
        token=token,
        show_border=bool(doc.show_border),
        show_title=bool(doc.show_title),
        dark_mode=dark_mode,
    )

    return {
        "url": url,
        "title": doc.title,
        "height": doc.iframe_height or (800 if resource_type == "dashboard" else 600),
        "resource_type": resource_type,
    }


@frappe.whitelist()
def get_dashboard_list() -> list[dict]:
    """
    Return all active Metabase Dashboards the current user has access to.

    Used by the Gallery page to list available dashboards.

    Returns:
        List of dicts with: name, title, description, dashboard_id
    """
    dashboards = frappe.get_all(
        "Metabase Dashboard",
        filters={"is_active": 1},
        fields=["name", "title", "description", "dashboard_id", "iframe_height"],
        order_by="title asc",
    )

    # Filter by role access
    user_roles = set(frappe.get_roles())
    accessible = []

    for dash in dashboards:
        allowed_roles = frappe.get_all(
            "Metabase Role",
            filters={"parent": dash.name, "parenttype": "Metabase Dashboard"},
            pluck="role",
        )

        # Empty allowed_roles = accessible to all logged-in users
        if not allowed_roles or user_roles.intersection(set(allowed_roles)):
            accessible.append(dash)

    return accessible


@frappe.whitelist()
def get_question_list() -> list[dict]:
    """
    Return all active Metabase Questions the current user has access to.

    Returns:
        List of dicts with: name, title, description, question_id
    """
    questions = frappe.get_all(
        "Metabase Question",
        filters={"is_active": 1},
        fields=["name", "title", "description", "question_id", "iframe_height"],
        order_by="title asc",
    )

    user_roles = set(frappe.get_roles())
    accessible = []

    for q in questions:
        allowed_roles = frappe.get_all(
            "Metabase Role",
            filters={"parent": q.name, "parenttype": "Metabase Question"},
            pluck="role",
        )

        if not allowed_roles or user_roles.intersection(set(allowed_roles)):
            accessible.append(q)

    return accessible


def _check_role_access(doc) -> None:
    """
    Check if the current user has a role that's in the document's
    allowed_roles list. Throws PermissionError if not.

    If allowed_roles is empty, all logged-in users are allowed.
    """
    if not doc.allowed_roles:
        return

    user_roles = set(frappe.get_roles())
    allowed = {r.role for r in doc.allowed_roles}

    if not user_roles.intersection(allowed):
        frappe.throw(
            f"You do not have permission to view '{doc.title}'.",
            frappe.PermissionError,
        )
