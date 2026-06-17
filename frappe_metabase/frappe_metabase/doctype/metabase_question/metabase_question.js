frappe.ui.form.on("Metabase Question", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Open Full Page"), function () {
                frappe.set_route("metabase-gallery", {
                    question: frm.doc.name,
                });
            });
        }
    },

    preview_question(frm) {
        if (frm.is_dirty()) {
            frappe.msgprint(__("Please save the document before previewing."));
            return;
        }

        let $preview = frm.fields_dict.embed_html.$wrapper;
        $preview.html(`
            <div style="text-align:center; padding:40px 0; color:var(--text-muted);">
                <i class="fa fa-spinner fa-spin fa-2x"></i>
                <p style="margin-top:10px;">Loading preview...</p>
            </div>
        `);

        frappe.call({
            method: "frappe_metabase.api.embed.get_embed_url",
            args: {
                doctype: "Metabase Question",
                name: frm.doc.name,
            },
            callback: function (r) {
                if (r.message && r.message.url) {
                    let height = frm.doc.iframe_height || 600;
                    $preview.html(`
                        <iframe
                            src="${r.message.url}"
                            frameborder="0"
                            style="width:100%; height:${height}px; border:none; border-radius:8px; margin-top:10px;"
                            allowtransparency>
                        </iframe>
                    `);
                } else {
                    $preview.html(`
                        <div class="text-danger" style="padding:20px;">
                            Failed to generate embed URL. Check Metabase Settings.
                        </div>
                    `);
                }
            },
        });
    },
});
