import frappe

from marina_costing.api import SUPPLIER_ROLES, can_manage_all_quotes


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access supplier costing.", frappe.PermissionError)

    roles = set(frappe.get_roles(frappe.session.user))
    if not can_manage_all_quotes() and not roles.intersection(SUPPLIER_ROLES):
        frappe.throw("You do not have access to supplier costing.", frappe.PermissionError)

    context.title = "Supplier Costing"
    context.no_cache = 1
    filters = {} if can_manage_all_quotes() else {"owner": frappe.session.user}
    context.pending_count = frappe.db.count(
        "Supplier Costing Quote", {**filters, "status": "Pending"}
    )
    context.approved_count = frappe.db.count(
        "Supplier Costing Quote", {**filters, "status": "Approved"}
    )
