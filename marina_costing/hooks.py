app_name = "marina_costing"
app_title = "Marina Costing"
app_publisher = "Marina Fashion Retail"
app_description = "Supplier costing quote management for ERPNext"
app_email = "info@marina.example"
app_license = "MIT"

required_apps = ["erpnext"]

before_install = "marina_costing.install.before_install"
after_install = "marina_costing.install.after_install"

website_route_rules = [
    {"from_route": "/supplier-costing", "to_route": "supplier-costing"},
]

web_include_css = [
    "/assets/marina_costing/css/marina_costing.css",
]

doc_events = {
    "Supplier Costing Quote": {
        "validate": "marina_costing.api.validate_supplier_costing_quote",
    }
}
