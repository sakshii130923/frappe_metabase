import frappe


def resolve_params(param_rows: list) -> dict:
    """
    Resolve locked parameters from child table rows into a flat dict
    suitable for the Metabase JWT payload.

    Each row has:
        - param_name: Metabase filter parameter name
        - source_type: "Static", "User Field", or "Frappe Method"
        - static_value: used when source_type is Static
        - user_field: field from User doctype (e.g. "company")
        - frappe_method: dotted path to a whitelisted method

    Returns:
        dict mapping param names to resolved values
    """
    params = {}

    for row in param_rows:
        value = _resolve_single_param(row)
        if value is not None:
            params[row.param_name] = value

    return params


def _resolve_single_param(row) -> str | list | None:
    """Resolve a single parameter row to its value."""

    if row.source_type == "Static":
        return row.static_value or None

    elif row.source_type == "User Field":
        return _resolve_user_field(row.user_field)

    elif row.source_type == "Frappe Method":
        return _resolve_frappe_method(row.frappe_method)

    return None


def _resolve_user_field(field_name: str) -> str | list | None:
    """
    Get a field value from the current user's User document.

    Supports dotted notation for linked documents:
        - "company" → User.company
        - "default_warehouse" → User.default_warehouse

    Also handles UserPermission-based fields:
        - If field_name starts with "perm:", looks up UserPermission
          e.g. "perm:Warehouse" → all Warehouse permissions for the user
    """
    if not field_name:
        return None

    user = frappe.session.user

    # Handle UserPermission lookups: "perm:Warehouse" → list of allowed warehouses
    if field_name.startswith("perm:"):
        doctype = field_name[5:].strip()
        permissions = frappe.get_all(
            "User Permission",
            filters={"user": user, "allow": doctype},
            pluck="for_value",
        )
        return permissions if permissions else None

    # Direct field from User doctype
    try:
        value = frappe.db.get_value("User", user, field_name)
        return value
    except Exception:
        frappe.log_error(
            f"Metabase Param: Could not resolve User field '{field_name}' "
            f"for user {user}"
        )
        return None


def _resolve_frappe_method(method_path: str) -> str | list | None:
    """
    Call a Frappe method by its dotted path and return the result.

    The method should:
        - Accept no arguments (user context is available via frappe.session)
        - Return a string, number, or list of strings
    """
    if not method_path:
        return None

    try:
        method = frappe.get_attr(method_path)
        result = method()
        return result
    except Exception as e:
        frappe.log_error(f"Metabase Param: Error calling method '{method_path}': {e}")
        return None
