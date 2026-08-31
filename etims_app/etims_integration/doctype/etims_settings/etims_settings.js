// Copyright (c) 2026, Naran Vekaria and contributors
// For license information, please see license.txt

// Which of "Sandbox Base URL" / "Production Base URL" is shown is driven by
// the `depends_on` on those fields in etims_settings.json (tied to the
// `environment` field) — kept out of this file to avoid duplicating that
// logic in two places.

frappe.ui.form.on("eTIMS Settings", {
	refresh(frm) {
		frm.add_custom_button(__("View KRA API Endpoint Reference"), () => {
			frappe.set_route("List", "eTIMS API Endpoint");
		});
	},
});
