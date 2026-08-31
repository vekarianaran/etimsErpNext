# Copyright (c) 2026, Naran Vekaria and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase

SAMPLE_REQUEST_FIELDS = """tin: Data, required
bhfId: Data, required
itemCd: Data, required
itemNm: Data, required"""

SAMPLE_RESPONSE_FIELDS = """resultCd: Data
resultMsg: Data
resultDt: Data"""

SAMPLE_REQUEST_PAYLOAD_TEMPLATE = """{
	"itemCd": "{{ doc.item_code }}",
	"itemNm": "{{ doc.item_name }}"
}"""


class TestETIMSAPIEndpoint(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _new_endpoint(self, **overrides):
		"""Build an unsaved eTIMS API Endpoint with valid sample values for
		every field. `triggering_doctype` points at `Item`, a real, always-
		present core doctype, so no fixture dependency is introduced."""
		values = {
			"doctype": "eTIMS API Endpoint",
			"endpoint_path": "saveItem",
			"http_method": "POST",
			"purpose": "Register or update an item's classification with KRA eTIMS.",
			"required_headers": "Content-Type, Authorization",
			"request_fields": SAMPLE_REQUEST_FIELDS,
			"response_fields": SAMPLE_RESPONSE_FIELDS,
			"is_enabled": 1,
			"status": "Planned",
			"triggering_doctype": "Item",
			"triggering_event": "on_update",
			"request_payload_template": SAMPLE_REQUEST_PAYLOAD_TEMPLATE,
			"result_storage": "eTIMS Submission Log.response_payload",
			"implementation_reference": "etims_app.etims_integration.item_submission.submit_item_to_kra",
		}
		values.update(overrides)
		return frappe.get_doc(values)

	def test_creates_with_valid_values_and_round_trips(self):
		doc = self._new_endpoint()
		doc.insert(ignore_permissions=True)

		reloaded = frappe.get_doc("eTIMS API Endpoint", doc.name)

		self.assertEqual(reloaded.endpoint_path, "saveItem")
		self.assertEqual(reloaded.http_method, "POST")
		self.assertEqual(
			reloaded.purpose, "Register or update an item's classification with KRA eTIMS."
		)
		self.assertEqual(reloaded.required_headers, "Content-Type, Authorization")
		self.assertEqual(reloaded.request_fields, SAMPLE_REQUEST_FIELDS)
		self.assertEqual(reloaded.response_fields, SAMPLE_RESPONSE_FIELDS)
		self.assertEqual(reloaded.is_enabled, 1)
		self.assertEqual(reloaded.status, "Planned")
		self.assertEqual(reloaded.triggering_doctype, "Item")
		self.assertEqual(reloaded.triggering_event, "on_update")
		self.assertEqual(reloaded.request_payload_template, SAMPLE_REQUEST_PAYLOAD_TEMPLATE)
		self.assertEqual(reloaded.result_storage, "eTIMS Submission Log.response_payload")
		self.assertEqual(
			reloaded.implementation_reference,
			"etims_app.etims_integration.item_submission.submit_item_to_kra",
		)

	def test_is_enabled_defaults_to_true(self):
		doc = frappe.get_doc(
			{
				"doctype": "eTIMS API Endpoint",
				"endpoint_path": "saveItemDefaultEnabled",
				"http_method": "POST",
			}
		)
		doc.insert(ignore_permissions=True)

		self.assertEqual(doc.is_enabled, 1)

	def test_request_payload_template_renders_to_valid_json(self):
		# This is the whole point of the fix this doctype went through: the
		# field must be genuinely executable (Jinja -> render -> json.loads),
		# not just descriptive text a human has to interpret.
		doc = self._new_endpoint(endpoint_path="saveItemTemplateRender")
		item = frappe.get_doc(
			{"doctype": "Item", "item_code": "TEST-ETIMS-ITEM", "item_name": "Test eTIMS Item"}
		)

		rendered = frappe.render_template(doc.request_payload_template, {"doc": item})
		payload = json.loads(rendered)

		self.assertEqual(payload["itemCd"], "TEST-ETIMS-ITEM")
		self.assertEqual(payload["itemNm"], "Test eTIMS Item")

	def test_status_defaults_to_documented(self):
		# Omit `status` entirely (rather than setting it then clearing it) so
		# the doctype's field default applies the way it does for a genuinely
		# new document — Frappe only applies field defaults at construction
		# time, not retroactively at insert().
		doc = frappe.get_doc(
			{
				"doctype": "eTIMS API Endpoint",
				"endpoint_path": "saveItemDefaultStatus",
				"http_method": "POST",
			}
		)
		doc.insert(ignore_permissions=True)

		self.assertEqual(doc.status, "Documented")

	def test_endpoint_path_uniqueness_enforced(self):
		first = self._new_endpoint(endpoint_path="selectCodeList")
		first.insert(ignore_permissions=True)

		second = self._new_endpoint(endpoint_path="selectCodeList")

		# `endpoint_path` is both a `unique: 1` field and the naming source
		# (`autoname: field:endpoint_path`), so a duplicate value collides on
		# the document's primary key (`name`) itself. Frappe's
		# `Document.db_insert` detects this as a primary key violation and
		# raises `frappe.DuplicateEntryError` (a subclass of
		# `frappe.ValidationError`) rather than a generic validation error.
		self.assertRaises(frappe.DuplicateEntryError, second.insert, ignore_permissions=True)
