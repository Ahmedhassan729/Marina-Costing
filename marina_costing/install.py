import frappe


def after_install():
    create_roles()


def before_install():
    create_roles()


def create_roles():
    for role_name in ["Supplier Costing User", "Supplier Costing Manager"]:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.desk_access = 1
            role.insert(ignore_permissions=True)
