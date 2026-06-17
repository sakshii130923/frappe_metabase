frappe.ui.form.on("Metabase Settings", {
    refresh(frm) {
        // Style the connection status
        if (frm.doc.connection_status) {
            let color = frm.doc.connection_status.includes("Connected")
                ? "green"
                : "red";
            frm.get_field("connection_status").$wrapper
                .find(".like-disabled-input")
                .css("color", `var(--${color}-500)`);
        }
    },

    test_connection(frm) {
        frappe.call({
            doc: frm.doc,
            method: "test_connection",
            freeze: true,
            freeze_message: "Testing connection to Metabase...",
            callback: function () {
                frm.reload_doc();
            },
        });
    },
});
