import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access supplier costing.", frappe.PermissionError)

    context.title = "Supplier Costing"
    context.no_cache = 1
    context.pending_count = frappe.db.count("Supplier Costing Quote", {"status": "Pending"})
    context.approved_count = frappe.db.count("Supplier Costing Quote", {"status": "Approved"})
