import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MANAGER_ROLES = {"Supplier Costing Manager", "System Manager"}


def can_manage_all_quotes():
    return bool(MANAGER_ROLES & set(frappe.get_roles(frappe.session.user)))


class SupplierCostingQuote(Document):
    def validate(self):
        self.validate_status_change()
        self.validate_internal_fields()
        self.validate_numeric_inputs()
        calculate_quote_totals(self)

    def validate_status_change(self):
        if self.is_new():
            if not can_manage_all_quotes() and self.status != "Pending":
                frappe.throw(_("New supplier quotes must start with Pending status."), frappe.PermissionError)
            return

        previous_status = frappe.db.get_value(self.doctype, self.name, "status")
        if previous_status != self.status and not can_manage_all_quotes():
            frappe.throw(_("Only a Supplier Costing Manager can change quote status."), frappe.PermissionError)

    def validate_internal_fields(self):
        if can_manage_all_quotes():
            return

        internal_fields = (
            "target_margin_percentage",
            "conversion_rate",
            "target_retail_price",
            "margin_percentage",
            "overhead_percentage",
            "review_lines",
        )
        if self.is_new():
            expected_defaults = {
                "target_margin_percentage": 0,
                "conversion_rate": 1,
                "target_retail_price": 0,
                "margin_percentage": 0,
                "overhead_percentage": 0,
            }
            has_internal_values = any(
                flt(self.get(fieldname)) != expected
                for fieldname, expected in expected_defaults.items()
            ) or bool(self.get("review_lines"))
        else:
            has_internal_values = any(self.has_value_changed(fieldname) for fieldname in internal_fields)

        if has_internal_values:
            frappe.throw(
                _("Only a Supplier Costing Manager can change internal costing fields."),
                frappe.PermissionError,
            )

    def validate_numeric_inputs(self):
        non_negative_fields = {
            "moq": _("MOQ"),
            "bulk_lead_time_days": _("Bulk Lead Time Days"),
            "sampling_charge_per_unit": _("Sampling Charge Per Unit"),
            "target_retail_price": _("Target Retail Price"),
        }
        for fieldname, label in non_negative_fields.items():
            if flt(self.get(fieldname)) < 0:
                frappe.throw(_("{0} cannot be negative.").format(label))

        for fieldname, label in {
            "target_margin_percentage": _("Target Margin %"),
            "margin_percentage": _("Supplier Margin %"),
            "overhead_percentage": _("Overhead %"),
        }.items():
            value = flt(self.get(fieldname))
            if value < 0 or value > 100:
                frappe.throw(_("{0} must be between 0 and 100.").format(label))

        if flt(self.conversion_rate) <= 0:
            frappe.throw(_("Conversion Rate must be greater than zero."))

        for row in self.get("cost_lines", []):
            if flt(row.consumption_per_garment) < 0 or flt(row.cost_per_unit) < 0:
                frappe.throw(_("Cost breakdown quantities and costs cannot be negative."))
            if flt(row.wastage_percentage) < 0 or flt(row.wastage_percentage) > 100:
                frappe.throw(_("Wastage % must be between 0 and 100."))

        for row in self.get("packaging_logistics", []):
            if flt(row.qty_per_garment) < 0 or flt(row.cost_per_unit) < 0:
                frappe.throw(_("Packaging quantities and costs cannot be negative."))

        for row in self.get("size_curve", []):
            if flt(row.sample_qty) < 0 or flt(row.bulk_qty) < 0:
                frappe.throw(_("Size quantities cannot be negative."))


def calculate_quote_totals(doc):
    direct_cost = 0
    for row in doc.get("cost_lines", []):
        row.cost_per_garment = (
            flt(row.consumption_per_garment)
            * (1 + flt(row.wastage_percentage) / 100)
            * flt(row.cost_per_unit)
        )
        direct_cost += flt(row.cost_per_garment)

    direct_cost += flt(doc.sampling_charge_per_unit)

    packaging_cost = 0
    for row in doc.get("packaging_logistics", []):
        row.cost_per_garment = flt(row.qty_per_garment) * flt(row.cost_per_unit)
        packaging_cost += flt(row.cost_per_garment)

    total_bulk_qty = sum(flt(row.bulk_qty) for row in doc.get("size_curve", []))
    for row in doc.get("size_curve", []):
        row.size_curve_percentage = (flt(row.bulk_qty) / total_bulk_qty * 100) if total_bulk_qty else 0

    doc.direct_cost = direct_cost
    doc.packaging_cost = packaging_cost
    conversion_rate = flt(doc.conversion_rate) or 1
    doc.target_unit_cost = (
        flt(doc.target_retail_price)
        * (1 - flt(doc.target_margin_percentage) / 100)
        / conversion_rate
    )

    base_cost = direct_cost + packaging_cost
    overhead_amount = base_cost * flt(doc.overhead_percentage) / 100
    doc.margin_amount = (base_cost + overhead_amount) * flt(doc.margin_percentage) / 100
    doc.quoted_unit_cost = base_cost + overhead_amount + flt(doc.margin_amount)
    doc.target_gap = flt(doc.quoted_unit_cost) - flt(doc.target_unit_cost)
    doc.estimated_gross_margin = (
        (flt(doc.target_retail_price) - flt(doc.quoted_unit_cost)) / flt(doc.target_retail_price) * 100
        if flt(doc.target_retail_price)
        else 0
    )


@frappe.whitelist()
def get_default_review_lines():
    return [
        "Target cost achieved or justified",
        "Fabric consumption plausible vs tech pack",
        "Wastage reasonable for print, stripe, placement, or embellishment",
        "MOQ and MCQ acceptable",
        "Sampling charge per unit entered when applicable",
        "Trims, labels, and branding included",
        "Packaging requirements included",
        "Testing and compliance included or clearly excluded",
        "Freight and commercial terms clear",
        "Quote validity date provided",
        "Negotiation or redesign decision recorded",
    ]
