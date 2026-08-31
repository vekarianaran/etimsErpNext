# Copyright (c) 2026, Naran Vekaria and contributors
# For license information, please see license.txt

"""Seed `eTIMS API Endpoint` with the KRA VSDC wire protocol, transcribed from
the vault's `eTIMS VSDC API Reference` note (reverse-engineered from KRA's own
reference client jar). Idempotent — safe to re-run.

Only `saveItem` has its "ERPNext Wiring" section filled in (status=Planned),
matching the currently-designed Item -> eTIMS registration flow. Every other
endpoint is seeded with `status=Documented` and blank wiring fields — the KRA
protocol is known, but no ERPNext-side integration has been designed for it
yet. Update the relevant row's wiring fields (don't re-run this patch) as each
future integration is designed/implemented.
"""

import frappe

ENDPOINTS = [
	{
		"endpoint_path": "selectInitVsdcInfo",
		"http_method": "POST",
		"purpose": (
			"Device initialization — issues cmcKey/intrlKey/signKey/sdcId/mrcNo for a "
			"given device serial number. One-shot per (tin, bhfId, dvcSrlNo) — returns "
			"error 902 'This device is installed' if already initialized, with no "
			"client- or API-level way to force reissue."
		),
		"required_headers": "none",
		"request_fields": "tin, bhfId, dvcSrlNo",
		"response_fields": (
			"resultCd, resultMsg, resultDt, data.info: tin, taxprNm, bsnsActv, bhfId, "
			"bhfNm, bhfOpenDt, prvncNm, dstrtNm, sctrNm, locDesc, hqYn, mgrNm, mgrTelNo, "
			"mgrEmail, sdcId, mrcNo, dvcId, intrlKey, signKey, cmcKey, lastPchsInvcNo, "
			"lastSaleRcptNo, lastInvcNo, lastSaleInvcNo, lastTrainInvcNo, "
			"lastProfrmInvcNo, lastCopyInvcNo, vatTyCd"
		),
	},
	{
		"endpoint_path": "selectInitInfoVsdcSeq",
		"http_method": "POST",
		"purpose": (
			"Pull current invoice/receipt sequence counters. Can be called before "
			"selectInitVsdcInfo has ever run, but cmcKey/intrlKey/signKey will be null "
			"until the device is actually initialized."
		),
		"required_headers": "none",
		"request_fields": "tin, bhfId, dvcSrlNo",
		"response_fields": "same data.info shape as selectInitVsdcInfo (sequence fields populated)",
	},
	{
		"endpoint_path": "selectServerTime",
		"http_method": "GET",
		"purpose": "Server time check (connectivity/clock-skew probe).",
		"required_headers": "none",
		"request_fields": "(no body)",
		"response_fields": "raw string response",
	},
	{
		"endpoint_path": "selectTestEcho",
		"http_method": "POST",
		"purpose": "Echo test.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, testStr",
		"response_fields": "data.testStr",
	},
	{
		"endpoint_path": "selectCodeList",
		"http_method": "POST",
		"purpose": "Reference code list (generic lookup codes).",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": (
			"data.clsList[] (CodeClassLVO: cdCls, cdClsNm, cdClsDesc, useYn, "
			"userDfnNm1-3), each with nested CodeDtlLVO: cd, cdNm, cdDesc, useYn, "
			"srtOrd, userDfnCd1-3"
		),
	},
	{
		"endpoint_path": "selectItemClsList",
		"http_method": "POST",
		"purpose": "Item classification code list (UNSPSC-style codes).",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": "data.itemClsList[]: itemClsCd, itemClsNm, itemClsLvl, taxTyCd, mjrTgYn, useYn",
	},
	{
		"endpoint_path": "selectCustomer",
		"http_method": "POST",
		"purpose": "Customer/taxpayer lookup by TIN.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, custmTin",
		"response_fields": "data.custList[]: tin, taxprNm, taxprSttsCd, prvncNm, dstrtNm, sctrNm, locDesc",
	},
	{
		"endpoint_path": "selectItemList",
		"http_method": "POST",
		"purpose": "Item master pull (KRA -> client).",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": (
			"data.itemList[]: tin, itemCd, itemClsCd, itemTyCd, itemNm, itemStdNm, "
			"orgnNatCd, pkgUnitCd, qtyUnitCd, taxTyCd, btchNo, regBhfId, bcd, dftPrc, "
			"grpPrcL1-5, addInfo, sftyQty, isrcAplcbYn, rraModYn, useYn"
		),
	},
	{
		"endpoint_path": "saveItem",
		"http_method": "POST",
		"purpose": "Register/update an item.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"tin, bhfId, itemCd, itemClsCd, itemTyCd, itemNm, itemStdNm, orgnNatCd, "
			"pkgUnitCd, qtyUnitCd, taxTyCd, btchNo, bcd, dftPrc, grpPrcL1-5, addInfo, "
			"sftyQty, isrcAplcbYn, useYn, regrId, regrNm, modrId, modrNm"
		),
		"response_fields": "resultCd/Msg/Dt, data=null",
		"status": "Planned",
		"triggering_doctype": "Item",
		"triggering_event": "on_update",
		"key_field_mapping": (
			"item_name -> itemNm\n"
			"item_name -> itemStdNm\n"
			"standard_rate -> dftPrc (also repeated across grpPrcL1-5)\n"
			"safety_stock -> sftyQty\n"
			"barcodes[0].barcode -> bcd (blank if no barcode row)\n"
			"disabled -> useYn (inverted: N if disabled else Y)\n"
			"etims_item_cls_code (planned field, Milestone 3/4) -> itemClsCd\n"
			"etims_item_type_code (planned field, Milestone 4, manual entry) -> itemTyCd\n"
			"etims_tax_type_code (planned field, Milestone 4, manual entry) -> taxTyCd\n"
			"etims_package_unit_code (planned field, Milestone 4, manual entry) -> pkgUnitCd\n"
			"etims_quantity_unit_code (planned field, Milestone 4, manual entry) -> qtyUnitCd\n"
			"etims_origin_nation_code (planned field, Milestone 4, default KE) -> orgnNatCd\n"
			"current session user (frappe.session.user) -> regrId/regrNm/modrId/modrNm\n"
			"(defaulted in the payload builder, not on the Item form: addInfo=\"\", "
			"isrcAplcbYn=\"N\", btchNo=\"\")"
		),
		"result_storage": (
			"eTIMS Submission Log (request_payload/response_payload/status); "
			"Item.etims_last_submission_status (planned field, Milestone 4) mirrors the "
			"latest status"
		),
	},
	{
		"endpoint_path": "saveItemComposition",
		"http_method": "POST",
		"purpose": "Register a composite/bundle item's components.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, itemCd, cpstItemCd, cpstQty, regrId, regrNm",
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "selectBhfList",
		"http_method": "POST",
		"purpose": "Branch (business location) list.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": (
			"data.bhfList[]: tin, bhfId, bhfNm, bhfSttsCd, prvncNm, dstrtNm, sctrNm, "
			"locDesc, mgrNm, mgrTelNo, mgrEmail, hqYn"
		),
	},
	{
		"endpoint_path": "saveBhfUser",
		"http_method": "POST",
		"purpose": "Register a branch user.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"tin, bhfId, userId, userNm, pwd, adrs, cntc, authCd, remark, useYn, "
			"regrId, regrNm, modrId, modrNm"
		),
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "saveBhfInsurance",
		"http_method": "POST",
		"purpose": "Register branch insurance details.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, isrccCd, isrccNm, isrcRt, useYn, regrId, regrNm, modrId, modrNm",
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "saveBhfCustomer",
		"http_method": "POST",
		"purpose": "Register a branch-linked customer.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"tin, bhfId, custNo, custTin, custNm, adrs, telNo, email, faxNo, useYn, "
			"remark, regrId, regrNm, modrId, modrNm"
		),
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "saveTrnsSalesVsdc",
		"http_method": "POST",
		"purpose": "Sales invoice submission (the core call).",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"Top-level (TrnsSalesSaveWrReq/ReqBody): tin, bhfId, invcNo, orgInvcNo, "
			"custTin, custNm, salesTyCd, rcptTyCd, pmtTyCd, salesSttsCd, cfmDt, salesDt, "
			"stockRlsDt, cnclReqDt, cnclDt, rfdDt, rfdRsnCd, totItemCnt, taxblAmtA-E, "
			"taxRtA-E, taxAmtA-E, totTaxblAmt, totTaxAmt, totAmt, prchrAcptcYn, remark, "
			"regrId, regrNm, modrId, modrNm, itemList[] (TrnsSalesSaveWrItem: itemSeq, "
			"itemCd, itemClsCd, itemNm, bcd, pkgUnitCd, pkg, qtyUnitCd, qty, prc, "
			"splyAmt, dcRt, dcAmt, isrccCd, isrccNm, isrcRt, isrcAmt, taxTyCd, taxblAmt, "
			"taxAmt, totAmt), plus a nested receipt object (TrnsSalesSaveWrReceipt) "
			"carrying the locally-computed intrlData/rcptSign and receipt-numbering "
			"fields (curRcptNo, totRcptNo, rptNo, rcptPbctDt, etc.) — computed before "
			"the call, not supplied raw. salesTyCd in {N,C,T,P}, rcptTyCd in {S,R}; "
			"only NS/NR/TS/TR/CS/CR/PS combinations are valid (error 834 otherwise)."
		),
		"response_fields": "resultCd/Msg/Dt, data: sdcId, mrcNo, rcptNo, totRcptNo, vsdcRcptPbctDate, intrlData, rcptSign",
	},
	{
		"endpoint_path": "selectTrnsPurchaseSalesList",
		"http_method": "POST",
		"purpose": "Pull supplier-reported sales that reference this buyer (for purchase confirmation).",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": (
			"data.saleList[] (TrnsPurchaseSales): spplrTin, spplrNm, spplrBhfId, "
			"spplrInvcNo, rcptTyCd, pmtTyCd, cfmDt, salesDt, stockRlsDt, totItemCnt, "
			"taxblAmtA-D, taxRtA-D, taxAmtA-D, totTaxblAmt, totTaxAmt, totAmt, remark, "
			"each with nested item list (itemSeq, itemCd, itemClsCd, itemNm, bcd, "
			"pkgUnitCd, pkg, qtyUnitCd, qty, prc, splyAmt, dcRt, dcAmt, taxTyCd, "
			"taxblAmt, taxAmt, totAmt)"
		),
	},
	{
		"endpoint_path": "insertTrnsPurchase",
		"http_method": "POST",
		"purpose": "Submit/confirm a purchase invoice.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"tin, bhfId, invcNo, orgInvcNo, spplrTin, spplrBhfId, spplrNm, spplrInvcNo, "
			"regTyCd, pchsTyCd, rcptTyCd, pmtTyCd, pchsSttsCd, cfmDt, pchsDt, wrhsDt, "
			"cnclReqDt, cnclDt, rfdDt, totItemCnt, taxblAmtA-E, taxRtA-E, taxAmtA-E, "
			"totTaxblAmt, totTaxAmt, totAmt, remark, regrId, regrNm, modrId, modrNm, "
			"itemList[] (itemSeq, itemCd, itemClsCd, itemNm, bcd, spplrItemClsCd, "
			"spplrItemCd, spplrItemNm, pkgUnitCd, pkg, qtyUnitCd, qty, prc, splyAmt, "
			"dcRt, dcAmt, taxblAmt, taxTyCd, taxAmt, totAmt, itemExprDt)"
		),
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "selectImportItemList",
		"http_method": "POST",
		"purpose": "Pull customs/import item declarations.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": (
			"data.itemList[] (ImportItem): taskCd, dclDe, itemSeq, dclNo, hsCd, itemNm, "
			"imptItemsttsCd, orgnNatCd, exptNatCd, pkg, pkgUnitCd, qty, qtyUnitCd, "
			"totWt, netWt, spplrNm, agntNm, invcFcurAmt, invcFcurCd, invcFcurExcrt"
		),
	},
	{
		"endpoint_path": "updateImportItem",
		"http_method": "POST",
		"purpose": "Update status of an import item declaration.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"tin, bhfId, taskCd, dclDe, itemSeq, hsCd, itemClsCd, itemCd, "
			"imptItemSttsCd, remark, modrId, modrNm"
		),
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "saveStockMaster",
		"http_method": "POST",
		"purpose": "Set/adjust an item's stock master quantity.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, itemCd, rsdQty, regrId, regrNm, modrId, modrNm",
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "selectStockMoveList",
		"http_method": "POST",
		"purpose": "Pull stock movement records.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": (
			"data.stockList[] (StockMove): custTin, custBhfId, sarNo, ocrnDt, "
			"totItemCnt, totTaxblAmt, totTaxAmt, totAmt, remark, itemList[] (itemSeq, "
			"itemCd, itemClsCd, itemNm, bcd, pkgUnitCd, pkg, qtyUnitCd, qty, itemExprDt, "
			"prc, splyAmt, totDcAmt, taxblAmt, taxTyCd, taxAmt, totAmt)"
		),
	},
	{
		"endpoint_path": "insertStockIO",
		"http_method": "POST",
		"purpose": "Submit a stock in/out movement.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": (
			"tin, bhfId, sarNo, orgSarNo, regTyCd, custTin, custNm, custBhfId, sarTyCd, "
			"ocrnDt, totItemCnt, totTaxblAmt, totTaxAmt, totAmt, remark, regrId, regrNm, "
			"modrId, modrNm, itemList[] (itemSeq, itemCd, itemClsCd, itemNm, bcd, "
			"pkgUnitCd, pkg, qtyUnitCd, qty, itemExprDt, prc, splyAmt, totDcAmt, "
			"taxblAmt, taxTyCd, taxAmt, totAmt)"
		),
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "selectNoticeList",
		"http_method": "POST",
		"purpose": "Pull KRA notices/announcements.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, lastReqDt",
		"response_fields": "data.noticeList[]: noticeNo, title, cont, dtlUrl, regrNm, regDt",
	},
	{
		"endpoint_path": "saveReportZ",
		"http_method": "POST",
		"purpose": "Submit daily Z-report.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "Full ReportZSaveReq rollup — not fully enumerated in the VSDC reference beyond this pointer.",
		"response_fields": "data=null",
	},
	{
		"endpoint_path": "checkReportZ",
		"http_method": "POST",
		"purpose": "Check/reconcile a submitted Z-report against KRA's totals.",
		"required_headers": "tin, bhfId, cmcKey",
		"request_fields": "tin, bhfId, rptDe",
		"response_fields": (
			"data: checkCode, plus zRpt/rcptRpt (ReportZCheckData: full set of "
			"*RcptPbctCnt/RcptOpnNo/RcptClsNo/SalesAmt/RfdAmt/SalesTaxAmt/RfdTaxAmt for "
			"normal/copy/training/proforma receipt categories)"
		),
	},
]


def execute():
	for endpoint in ENDPOINTS:
		if frappe.db.exists("eTIMS API Endpoint", endpoint["endpoint_path"]):
			continue
		doc = frappe.get_doc({"doctype": "eTIMS API Endpoint", **endpoint})
		doc.insert(ignore_permissions=True)
