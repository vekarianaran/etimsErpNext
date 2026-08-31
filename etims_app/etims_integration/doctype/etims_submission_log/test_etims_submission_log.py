# Copyright (c) 2026, Naran Vekaria and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

SAMPLE_REQUEST_PAYLOAD = '{"itemCd": "KE1NTXU0000001", "itemNm": "Test Item"}'
SAMPLE_RESPONSE_PAYLOAD = '{"resultCd": "000", "resultMsg": "Successful"}'


class TestETIMSSubmissionLog(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _new_log(self, **overrides):
		"""Build an unsaved eTIMS Submission Log with valid sample values for
		every field. `reference_name` deliberately points at a made-up Item
		code rather than a real inserted Item — link existence isn't
		validated here (`ignore_links`) since this doctype is standalone/inert
		for this milestone and shouldn't depend on ERPNext fixture data being
		present in the test site."""
		values = {
			"doctype": "eTIMS Submission Log",
			"reference_doctype": "Item",
			"reference_name": "TEST-ITEM-0001",
			"submission_type": "Item Registration",
			"status": "Pending",
			"attempt_count": 0,
			"next_retry_at": "2026-09-01 08:00:00",
			"idempotency_key": frappe.generate_hash(length=20),
			"request_payload": SAMPLE_REQUEST_PAYLOAD,
			"response_payload": SAMPLE_RESPONSE_PAYLOAD,
			"error_message": "Sample error message for round-trip testing.",
		}
		values.update(overrides)
		doc = frappe.get_doc(values)
		doc.flags.ignore_links = True
		return doc

	def test_creates_with_valid_values_and_round_trips(self):
		doc = self._new_log()
		doc.insert(ignore_permissions=True)

		reloaded = frappe.get_doc("eTIMS Submission Log", doc.name)

		self.assertEqual(reloaded.reference_doctype, "Item")
		self.assertEqual(reloaded.reference_name, "TEST-ITEM-0001")
		self.assertEqual(reloaded.submission_type, "Item Registration")
		self.assertEqual(reloaded.status, "Pending")
		self.assertEqual(reloaded.attempt_count, 0)
		self.assertEqual(str(reloaded.next_retry_at), "2026-09-01 08:00:00")
		self.assertEqual(reloaded.idempotency_key, doc.idempotency_key)
		self.assertEqual(reloaded.request_payload, SAMPLE_REQUEST_PAYLOAD)
		self.assertEqual(reloaded.response_payload, SAMPLE_RESPONSE_PAYLOAD)
		self.assertEqual(reloaded.error_message, "Sample error message for round-trip testing.")

	def test_status_defaults_to_pending(self):
		# Omit `status` entirely (rather than setting it then clearing it) so
		# the doctype's field default applies the way it does for a genuinely
		# new document — Frappe only applies field defaults at construction
		# time, not retroactively at insert().
		doc = frappe.get_doc(
			{
				"doctype": "eTIMS Submission Log",
				"reference_doctype": "Item",
				"reference_name": "TEST-ITEM-0001",
				"submission_type": "Item Registration",
				"idempotency_key": frappe.generate_hash(length=20),
			}
		)
		doc.flags.ignore_links = True
		doc.insert(ignore_permissions=True)

		self.assertEqual(doc.status, "Pending")

	def test_idempotency_key_uniqueness_enforced(self):
		shared_key = frappe.generate_hash(length=20)

		first = self._new_log(idempotency_key=shared_key)
		first.insert(ignore_permissions=True)

		second = self._new_log(idempotency_key=shared_key)

		self.assertRaises(frappe.ValidationError, second.insert, ignore_permissions=True)
