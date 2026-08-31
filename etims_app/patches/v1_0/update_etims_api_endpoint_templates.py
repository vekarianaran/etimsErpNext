# Copyright (c) 2026, Naran Vekaria and contributors
# For license information, please see license.txt

"""Backfill `eTIMS API Endpoint.request_payload_template` (Jinja JSON) and
`is_enabled` for all 25 endpoints seeded by `seed_etims_api_endpoints.py`.

This is a separate patch, not an edit to the original seed patch, because
Frappe records executed patches in `tabPatch Log` and will not rerun one just
because its source changed — a site where the original patch already ran
needs this new patch to actually pick up the fix. Runs as an upsert (update if
the row exists, insert if it somehow doesn't) so it's safe on both fresh and
already-seeded sites.

Template convention: static values are literal; per-document values use
`{{ doc.<field> }}`; settings-derived values use `{{ settings.<field> }}`
(the `eTIMS Settings` singleton). Fields with no ERPNext-side mapping decided
yet (every endpoint except `saveItem`) use a generic placeholder variable
named after the KRA field, to be supplied by whichever function eventually
calls that endpoint — not a fabricated doc/settings reference.

Endpoints intentionally left without a template (still `request_payload_template`
blank after this patch): `selectServerTime` (bare GET, no body),
`saveTrnsSalesVsdc`/`insertTrnsPurchase`/`insertStockIO` (nested itemList[]
requiring a real per-item Jinja loop once that ERPNext mapping is designed),
`saveReportZ` (request body not fully enumerated in the VSDC reference).
"""

import frappe

# fmt: off
TEMPLATES = {
	"selectInitVsdcInfo": (
		'{\n'
		'\t"tin": "{{ settings.kra_pin }}",\n'
		'\t"bhfId": "{{ settings.branch_id }}",\n'
		'\t"dvcSrlNo": "{{ settings.device_serial_number }}"\n'
		'}'
	),
	"selectInitInfoVsdcSeq": (
		'{\n'
		'\t"tin": "{{ settings.kra_pin }}",\n'
		'\t"bhfId": "{{ settings.branch_id }}",\n'
		'\t"dvcSrlNo": "{{ settings.device_serial_number }}"\n'
		'}'
	),
	"selectTestEcho": (
		'{\n'
		'\t"testStr": "{{ test_str }}"\n'
		'}'
	),
	"selectCodeList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"selectItemClsList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"selectCustomer": (
		'{\n'
		'\t"custmTin": "{{ customer_tin }}"\n'
		'}'
	),
	"selectItemList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"saveItem": (
		'{\n'
		'\t"itemCd": "{{ doc.item_code }}",\n'
		'\t"itemClsCd": "{{ doc.etims_item_cls_code }}",\n'
		'\t"itemTyCd": "{{ doc.etims_item_type_code }}",\n'
		'\t"itemNm": "{{ doc.item_name }}",\n'
		'\t"itemStdNm": "{{ doc.item_name }}",\n'
		'\t"orgnNatCd": "{{ doc.etims_origin_nation_code }}",\n'
		'\t"pkgUnitCd": "{{ doc.etims_package_unit_code }}",\n'
		'\t"qtyUnitCd": "{{ doc.etims_quantity_unit_code }}",\n'
		'\t"taxTyCd": "{{ doc.etims_tax_type_code }}",\n'
		'\t"btchNo": "",\n'
		'\t"bcd": "{{ doc.barcodes[0].barcode if doc.barcodes else \'\' }}",\n'
		'\t"dftPrc": "{{ doc.standard_rate }}",\n'
		'\t"grpPrcL1": "{{ doc.standard_rate }}",\n'
		'\t"grpPrcL2": "{{ doc.standard_rate }}",\n'
		'\t"grpPrcL3": "{{ doc.standard_rate }}",\n'
		'\t"grpPrcL4": "{{ doc.standard_rate }}",\n'
		'\t"grpPrcL5": "{{ doc.standard_rate }}",\n'
		'\t"addInfo": "",\n'
		'\t"sftyQty": "{{ doc.safety_stock }}",\n'
		'\t"isrcAplcbYn": "N",\n'
		'\t"useYn": "{{ \'N\' if doc.disabled else \'Y\' }}",\n'
		'\t"regrId": "{{ frappe.session.user }}",\n'
		'\t"regrNm": "{{ frappe.session.user }}",\n'
		'\t"modrId": "{{ frappe.session.user }}",\n'
		'\t"modrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"saveItemComposition": (
		'{\n'
		'\t"itemCd": "{{ item_cd }}",\n'
		'\t"cpstItemCd": "{{ composite_item_cd }}",\n'
		'\t"cpstQty": "{{ composite_qty }}",\n'
		'\t"regrId": "{{ frappe.session.user }}",\n'
		'\t"regrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"selectBhfList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"saveBhfUser": (
		'{\n'
		'\t"userId": "{{ user_id }}",\n'
		'\t"userNm": "{{ user_name }}",\n'
		'\t"pwd": "{{ password }}",\n'
		'\t"adrs": "{{ address }}",\n'
		'\t"cntc": "{{ contact }}",\n'
		'\t"authCd": "{{ auth_cd }}",\n'
		'\t"remark": "{{ remark }}",\n'
		'\t"useYn": "{{ use_yn }}",\n'
		'\t"regrId": "{{ frappe.session.user }}",\n'
		'\t"regrNm": "{{ frappe.session.user }}",\n'
		'\t"modrId": "{{ frappe.session.user }}",\n'
		'\t"modrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"saveBhfInsurance": (
		'{\n'
		'\t"isrccCd": "{{ insurance_cd }}",\n'
		'\t"isrccNm": "{{ insurance_nm }}",\n'
		'\t"isrcRt": "{{ insurance_rate }}",\n'
		'\t"useYn": "{{ use_yn }}",\n'
		'\t"regrId": "{{ frappe.session.user }}",\n'
		'\t"regrNm": "{{ frappe.session.user }}",\n'
		'\t"modrId": "{{ frappe.session.user }}",\n'
		'\t"modrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"saveBhfCustomer": (
		'{\n'
		'\t"custNo": "{{ customer_no }}",\n'
		'\t"custTin": "{{ customer_tin }}",\n'
		'\t"custNm": "{{ customer_nm }}",\n'
		'\t"adrs": "{{ address }}",\n'
		'\t"telNo": "{{ phone }}",\n'
		'\t"email": "{{ email }}",\n'
		'\t"faxNo": "{{ fax_no }}",\n'
		'\t"useYn": "{{ use_yn }}",\n'
		'\t"remark": "{{ remark }}",\n'
		'\t"regrId": "{{ frappe.session.user }}",\n'
		'\t"regrNm": "{{ frappe.session.user }}",\n'
		'\t"modrId": "{{ frappe.session.user }}",\n'
		'\t"modrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"selectTrnsPurchaseSalesList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"selectImportItemList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"updateImportItem": (
		'{\n'
		'\t"taskCd": "{{ task_cd }}",\n'
		'\t"dclDe": "{{ declaration_date }}",\n'
		'\t"itemSeq": "{{ item_seq }}",\n'
		'\t"hsCd": "{{ hs_cd }}",\n'
		'\t"itemClsCd": "{{ item_cls_cd }}",\n'
		'\t"itemCd": "{{ item_cd }}",\n'
		'\t"imptItemSttsCd": "{{ import_item_status_cd }}",\n'
		'\t"remark": "{{ remark }}",\n'
		'\t"modrId": "{{ frappe.session.user }}",\n'
		'\t"modrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"saveStockMaster": (
		'{\n'
		'\t"itemCd": "{{ item_cd }}",\n'
		'\t"rsdQty": "{{ residual_qty }}",\n'
		'\t"regrId": "{{ frappe.session.user }}",\n'
		'\t"regrNm": "{{ frappe.session.user }}",\n'
		'\t"modrId": "{{ frappe.session.user }}",\n'
		'\t"modrNm": "{{ frappe.session.user }}"\n'
		'}'
	),
	"selectStockMoveList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"selectNoticeList": (
		'{\n'
		'\t"lastReqDt": "{{ last_req_dt }}"\n'
		'}'
	),
	"checkReportZ": (
		'{\n'
		'\t"rptDe": "{{ report_date }}"\n'
		'}'
	),
}
# fmt: on

# Endpoints with no request body at all, or whose body is too complex
# (nested arrays/objects) to safely auto-populate without fabricating an
# undesigned ERPNext mapping. Still get `is_enabled=1`, just no template.
NO_TEMPLATE = [
	"selectServerTime",
	"saveTrnsSalesVsdc",
	"insertTrnsPurchase",
	"insertStockIO",
	"saveReportZ",
]

ALL_ENDPOINT_PATHS = list(TEMPLATES.keys()) + NO_TEMPLATE


def execute():
	for endpoint_path in ALL_ENDPOINT_PATHS:
		if not frappe.db.exists("eTIMS API Endpoint", endpoint_path):
			# The original seed patch (or a future one) hasn't created this row
			# yet — nothing to backfill onto.
			continue

		doc = frappe.get_doc("eTIMS API Endpoint", endpoint_path)
		doc.is_enabled = 1
		if endpoint_path in TEMPLATES:
			doc.request_payload_template = TEMPLATES[endpoint_path]
		doc.save(ignore_permissions=True)
