# Copyright (c) 2026, Naran Vekaria and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from etims_app.etims_integration.crypto_utils import decrypt_value, encrypt_value

PAIR_FIELDS = [
	("sdc_id", "sdc_id_encrypted"),
	("device_serial_number", "device_serial_number_encrypted"),
	("mrc_no", "mrc_no_encrypted"),
	("cmc_key", "cmc_key_encrypted"),
	("intrl_key", "intrl_key_encrypted"),
	("sign_key", "sign_key_encrypted"),
]


class eTIMSSettings(Document):
	def validate(self):
		self.sync_encrypted_decrypted_pairs()

	def sync_encrypted_decrypted_pairs(self):
		"""Whichever field in a decrypted/encrypted pair was just edited,
		compute the other one. If both were edited in the same save, the
		encrypted field wins (it's treated as the value coming in from
		KRA/the keystore)."""
		before = self.get_doc_before_save()
		aes_key = None

		for decrypted_field, encrypted_field in PAIR_FIELDS:
			new_decrypted = self._field_value(decrypted_field)
			new_encrypted = self._field_value(encrypted_field)
			old_decrypted = self._field_value(decrypted_field, before) if before else ""
			old_encrypted = self._field_value(encrypted_field, before) if before else ""

			decrypted_changed = new_decrypted != old_decrypted
			encrypted_changed = new_encrypted != old_encrypted

			if not decrypted_changed and not encrypted_changed:
				continue
			if not new_decrypted and not new_encrypted:
				continue

			if aes_key is None:
				aes_key = self.aes_key
				if not aes_key:
					frappe.throw(frappe._("AES Key is required to sync encrypted/decrypted eTIMS values."))

			if encrypted_changed:
				self.set(decrypted_field, self._decrypt(encrypted_field, new_encrypted, aes_key))
			elif decrypted_changed:
				self.set(encrypted_field, self._encrypt(decrypted_field, new_decrypted, aes_key))

	def _field_value(self, fieldname, doc=None):
		target = doc or self
		return target.get(fieldname) or ""

	def _decrypt(self, fieldname, value, aes_key):
		try:
			return decrypt_value(value, aes_key)
		except Exception:
			frappe.throw(
				frappe._(
					"Could not decrypt '{0}' — check the AES Key and that the value is valid Base64 ciphertext."
				).format(self.meta.get_label(fieldname))
			)

	def _encrypt(self, fieldname, value, aes_key):
		try:
			return encrypt_value(value, aes_key)
		except Exception:
			frappe.throw(
				frappe._("Could not encrypt '{0}' — check the AES Key.").format(self.meta.get_label(fieldname))
			)

	def get_active_base_url(self):
		"""Return whichever base URL is active for the configured environment."""
		return self.production_base_url if self.environment == "Production" else self.sandbox_base_url
