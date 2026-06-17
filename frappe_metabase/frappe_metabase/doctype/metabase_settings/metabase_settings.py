import frappe
from frappe.model.document import Document


class MetabaseSettings(Document):

    def validate(self):
        # Strip trailing slash from server URL
        if self.server_url:
            self.server_url = self.server_url.rstrip("/")

    @frappe.whitelist()
    def test_connection(self):
        """Test connectivity to the Metabase instance."""
        from frappe_metabase.utils.connection import test_metabase_connection

        success, message = test_metabase_connection(
            self.server_url, self.get_password("secret_key")
        )

        self.connection_status = message
        self.save()

        if success:
            frappe.msgprint(message, indicator="green", title="Metabase Connection")
        else:
            frappe.msgprint(message, indicator="red", title="Metabase Connection")
