import frappe
from frappe.model.document import Document


class MetabaseDashboard(Document):

    def validate(self):
        if self.dashboard_id and self.dashboard_id < 1:
            frappe.throw("Dashboard ID must be a positive integer.")

    def on_update(self):
        # Clear embed cache when dashboard config changes
        cache_key = f"metabase_embed:dashboard:{self.name}"
        frappe.cache.delete_value(cache_key)

    @frappe.whitelist()
    def get_embed_url(self):
        """Generate and return the embed URL for this dashboard."""
        from frappe_metabase.api.embed import get_embed_url

        return get_embed_url(doctype="Metabase Dashboard", name=self.name)
