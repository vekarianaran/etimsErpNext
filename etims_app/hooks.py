from . import __version__ as app_version

app_name = "etims_app"
app_title = "eTIMS Integration"
app_publisher = "Aaron Vekaria"
app_description = "ERPNext integration with Kenya Revenue Authority's eTIMS"
app_email = "vekarianaran@gmail.com"
app_license = "mit"

# Includes in <head>
# ------------------
# app_include_css = "/assets/etims_app/css/etims_app.css"
# app_include_js = "/assets/etims_app/js/etims_app.js"

# Document Events
# ---------------
# Hook on document methods and events, e.g. submitting a Sales Invoice
# triggers an eTIMS submission.
# doc_events = {
#     "Sales Invoice": {
#         "on_submit": "etims_app.etims_integration.utils.submit_invoice_to_etims",
#         "on_cancel": "etims_app.etims_integration.utils.cancel_invoice_on_etims",
#     },
# }

# Scheduled Tasks
# ---------------
# scheduler_events = {
#     "cron": {
#         "*/15 * * * *": [
#             "etims_app.etims_integration.utils.retry_queued_submissions",
#         ]
#     },
# }
