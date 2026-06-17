frappe.pages["metabase-gallery"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Metabase Gallery"),
		single_column: true,
	});

	page.wrapper = wrapper;
	page.$body = $(wrapper).find(".layout-main-section");

	// Initial load based on URL params
	let route_params = frappe.utils.get_query_params();
	if (route_params.dashboard) {
		load_embed(page, "Metabase Dashboard", route_params.dashboard, true);
	} else if (route_params.question) {
		load_embed(page, "Metabase Question", route_params.question, true);
	} else {
		load_gallery(page, false);
	}

	// Listen to browser popstate to handle back/forward navigation
	$(window).on("popstate.metabase_gallery", function() {
		let params = frappe.utils.get_query_params();
		if (params.dashboard) {
			load_embed(page, "Metabase Dashboard", params.dashboard, false);
		} else if (params.question) {
			load_embed(page, "Metabase Question", params.question, false);
		} else {
			load_gallery(page, false);
		}
	});
};

function load_gallery(page, update_history = true) {
	page.set_title(__("Metabase Gallery"));
	page.clear_actions();

	if (update_history) {
		window.history.pushState(null, "", "/app/metabase-gallery");
	}

	page.$body.html(`
		<div style="text-align:center; padding:60px 0; color:var(--text-muted);">
			<i class="fa fa-spinner fa-spin fa-2x"></i>
			<p style="margin-top:10px;">${__("Loading analytics...")}</p>
		</div>
	`);

	Promise.all([
		frappe.xcall("frappe_metabase.api.embed.get_dashboard_list"),
		frappe.xcall("frappe_metabase.api.embed.get_question_list"),
	])
		.then(([dashboards, questions]) => {
			render_gallery(page, dashboards || [], questions || []);
		})
		.catch((err) => {
			page.$body.html(`
				<div style="text-align:center; padding:60px 0;">
					<i class="fa fa-exclamation-circle fa-2x text-danger"></i>
					<p class="text-danger" style="margin-top:10px;">
						${__("Failed to load analytics. Make sure Metabase Settings are configured.")}
					</p>
				</div>
			`);
		});
}

function render_gallery(page, dashboards, questions) {
	if (!dashboards.length && !questions.length) {
		page.$body.html(`
			<div style="text-align:center; padding:60px 0; color:var(--text-muted);">
				<i class="fa fa-bar-chart fa-3x"></i>
				<h4 style="margin-top:15px;">${__("No Dashboards Yet")}</h4>
				<p>${__("Create a")} <a href="/app/metabase-dashboard/new">${__("Metabase Dashboard")}</a>
				   ${__("or")} <a href="/app/metabase-question/new">${__("Metabase Question")}</a> ${__("to get started.")}</p>
			</div>
		`);
		return;
	}

	let html = '<div class="metabase-gallery-grid">';

	if (dashboards.length) {
		html += `<h5 class="metabase-gallery-section">${__("Dashboards")}</h5>`;
		html += '<div class="metabase-gallery-cards">';
		dashboards.forEach((d) => {
			html += render_card(d, "Metabase Dashboard", "fa-th-large");
		});
		html += "</div>";
	}

	if (questions.length) {
		html += `<h5 class="metabase-gallery-section">${__("Questions")}</h5>`;
		html += '<div class="metabase-gallery-cards">';
		questions.forEach((q) => {
			html += render_card(q, "Metabase Question", "fa-line-chart");
		});
		html += "</div>";
	}

	html += "</div>";
	page.$body.html(html);

	// Bind click handlers
	page.$body.find(".metabase-card").on("click", function () {
		let doctype = $(this).data("doctype");
		let name = $(this).data("name");
		load_embed(page, doctype, name, true);
	});
}

function render_card(item, doctype, icon) {
	let desc = item.description
		? `<p class="metabase-card-desc">${frappe.utils.escape_html(item.description)}</p>`
		: "";

	return `
		<div class="metabase-card" data-doctype="${doctype}" data-name="${frappe.utils.escape_html(item.name)}">
			<div class="metabase-card-icon">
				<i class="fa ${icon}"></i>
			</div>
			<div class="metabase-card-body">
				<h6 class="metabase-card-title">${frappe.utils.escape_html(item.title)}</h6>
				${desc}
			</div>
		</div>
	`;
}

function load_embed(page, doctype, name, update_history = true) {
	page.set_title(__("Metabase Gallery"));

	// Add back button
	page.clear_actions();
	page.set_secondary_action(__("← Back to Gallery"), function () {
		load_gallery(page, true);
	});

	if (update_history) {
		let param = doctype === "Metabase Dashboard" ? "dashboard" : "question";
		window.history.pushState(null, "", `/app/metabase-gallery?${param}=${encodeURIComponent(name)}`);
	}

	page.$body.html(`
		<div style="text-align:center; padding:60px 0; color:var(--text-muted);">
			<i class="fa fa-spinner fa-spin fa-2x"></i>
			<p style="margin-top:10px;">${__("Loading embed...")}</p>
		</div>
	`);

	frappe.xcall("frappe_metabase.api.embed.get_embed_url", {
		doctype: doctype,
		name: name,
	})
		.then((result) => {
			if (result && result.url) {
				let height = result.height || 800;
				page.$body.html(`
					<div class="metabase-embed-container">
						<h3 class="metabase-embed-title">${frappe.utils.escape_html(result.title)}</h3>
						<iframe
							src="${result.url}"
							frameborder="0"
							class="metabase-embed-iframe"
							style="width:100%; height:${height}px; border:none; border-radius:8px;"
							allowtransparency>
						</iframe>
					</div>
				`);
			}
		})
		.catch((err) => {
			page.$body.html(`
				<div style="text-align:center; padding:60px 0;">
					<i class="fa fa-exclamation-circle fa-2x text-danger"></i>
					<p class="text-danger" style="margin-top:10px;">
						${err.message || __("Failed to load embed. Check permissions and Metabase Settings.")}
					</p>
				</div>
			`);
		});
}
