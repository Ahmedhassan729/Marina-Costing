frappe.ui.form.on("Supplier Costing Quote", {
    setup(frm) {
        frm.set_query("supplier", () => ({ filters: { disabled: 0 } }));
        frm.set_query("item", () => ({ filters: { disabled: 0 } }));
    },

    refresh(frm) {
        frm.set_value("brand", "Marina Fashion Retail");

        if (frm.is_new() && !frm.doc.review_lines?.length) {
            frappe.call({
                method: "marina_costing.marina_costing.doctype.supplier_costing_quote.supplier_costing_quote.get_default_review_lines",
                callback(response) {
                    (response.message || []).forEach((check) => {
                        const row = frm.add_child("review_lines");
                        row.check_item = check;
                        row.review_status = "Pending";
                    });
                    frm.refresh_field("review_lines");
                },
            });
        }

        if (!frm.is_new()) {
            frm.add_custom_button(__("Close Quote"), () => {
                frm.set_value("status", "Closed");
                frm.save();
            });
            frm.add_custom_button(__("Reopen"), () => {
                frm.set_value("status", "Pending");
                frm.save();
            });
        }
    },
});

