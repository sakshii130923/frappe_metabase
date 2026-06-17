/**
 * Frappe Metabase — Global Embed Helper
 *
 * Use from any Frappe page or form:
 *
 *   frappe.metabase.embed({
 *       container: ".my-container",    // jQuery selector or element
 *       doctype: "Metabase Dashboard", // or "Metabase Question"
 *       name: "Sales Overview",        // document name
 *       height: 800,                   // optional, overrides doctype setting
 *   });
 */

frappe.provide("frappe.metabase");

frappe.metabase.embed = function (opts) {
    if (!opts.container || !opts.doctype || !opts.name) {
        console.error(
            "frappe.metabase.embed requires: container, doctype, name"
        );
        return;
    }

    let $container =
        typeof opts.container === "string"
            ? $(opts.container)
            : $(opts.container);

    if (!$container.length) {
        console.error("frappe.metabase.embed: container not found");
        return;
    }

    // Show loading
    $container.html(`
        <div class="metabase-loading">
            <i class="fa fa-spinner fa-spin"></i>
            <p>Loading analytics...</p>
        </div>
    `);

    frappe.xcall("frappe_metabase.api.embed.get_embed_url", {
        doctype: opts.doctype,
        name: opts.name,
    })
        .then(function (result) {
            if (result && result.url) {
                let height = opts.height || result.height || 800;
                $container.html(
                    `<iframe
                        src="${result.url}"
                        frameborder="0"
                        class="metabase-embed-iframe"
                        style="width:100%; height:${height}px; border:none; border-radius:8px;"
                        allowtransparency>
                    </iframe>`
                );
            } else {
                $container.html(
                    '<div class="text-danger" style="padding:20px;">Failed to load Metabase embed.</div>'
                );
            }
        })
        .catch(function (err) {
            $container.html(
                `<div class="text-danger" style="padding:20px;">
                    ${err.message || "Error loading Metabase embed."}
                </div>`
            );
        });
};
