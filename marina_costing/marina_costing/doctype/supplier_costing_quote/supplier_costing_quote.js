frappe.ui.form.on("Supplier Costing Quote", {
    refresh(frm) {
        frm.trigger("calculate_target_unit_cost");
        const can_manage = ["Supplier Costing Manager", "System Manager"].some(
            (role) => frappe.user_roles.includes(role)
        );

        if (frm.is_new() && can_manage && !frm.doc.review_lines?.length) {
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

        if (!frm.is_new() && can_manage) {
            frm.add_custom_button(__("Approve"), () => {
                frm.set_value("status", "Approved");
                frm.save();
            });
            frm.add_custom_button(__("Reject"), () => {
                frm.set_value("status", "Rejected");
                frm.save();
            });
            frm.add_custom_button(__("Cancel"), () => {
                frm.set_value("status", "Cancelled");
                frm.save();
            });
            frm.add_custom_button(__("Set Pending"), () => {
                frm.set_value("status", "Pending");
                frm.save();
            });
        }
    },

    target_retail_price(frm) {
        frm.trigger("calculate_target_unit_cost");
    },

    target_margin_percentage(frm) {
        frm.trigger("calculate_target_unit_cost");
    },

    conversion_rate(frm) {
        frm.trigger("calculate_target_unit_cost");
    },

    calculate_target_unit_cost(frm) {
        const conversion_rate = flt(frm.doc.conversion_rate) || 1;
        const target_unit_cost =
            (flt(frm.doc.target_retail_price) *
                (1 - flt(frm.doc.target_margin_percentage) / 100)) /
            conversion_rate;

        frm.set_value("target_unit_cost", target_unit_cost);
    },
});
