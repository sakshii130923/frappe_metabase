import frappe
from frappe.model.document import Document


class MetabaseQuestion(Document):
    def validate(self):
        if self.question_id and self.question_id < 1:
            frappe.throw("Question ID must be a positive integer.")

    def on_update(self):
        cache_key = f"metabase_embed:question:{self.name}"
        frappe.cache.delete_value(cache_key)

    @frappe.whitelist()
    def get_embed_url(self):
        """Generate and return the embed URL for this question."""
        from frappe_metabase.api.embed import get_embed_url

        return get_embed_url(doctype="Metabase Question", name=self.name)
