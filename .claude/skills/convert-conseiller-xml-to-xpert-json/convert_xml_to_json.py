#!/usr/bin/env python3
"""Convertit un TaskSpec XML de Conseiller (WPF legacy) en requête de génération JSON Xpert.

Cible : le corps POST des routes de génération de ReportManagerApi
(ex. POST /api/v1/order-entries/reports). Le mapping est dérivé de paires XML/JSON
réelles + des enums protobuf (report_definitions.proto). Voir SKILL.md.

Usage:
    python convert_xml_to_json.py input.xml [-o output.json] \
        [--session-id UUID] [--session-token "Bearer ..."] [--name ReportBatchService]

sessionId / sessionToken n'existent PAS dans le XML (jetons runtime). Sans flags,
ils sortent en chaîne vide + un avertissement sur stderr.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET

# ---- Tables d'enum (report_definitions.proto — source de vérité) ----
GENERATION_OUTPUT = {
    "0": "GEN_OUT_UNSPECIFIED",
    "1": "GEN_OUT_SINGLE_RESULT_FILE",
    "2": "GEN_OUT_MULTI_RESULT_FILE",
    "3": "GEN_OUT_EMAIL",
    "4": "GEN_OUT_DEBUG_DATASET",
    "5": "GEN_OUT_DEBUG_PACKAGE",
    "6": "GEN_OUT_TASK_PREVIEW",
}
RESULT_FILE_FORMAT = {
    "0": "RESULT_FILE_FORMAT_NONE",
    "1": "RESULT_FILE_FORMAT_PDF",
    "2": "RESULT_DATASET",
    "3": "RESULT_DEBUG_PACKAGE",
    "4": "RESULT_TASK_PREVIEW",
}
SORT_ORDER = {
    "0": "SORT_ORDER_UNSPECIFIED",
    "1": "SORT_ORDER_ASCENDING",
    "2": "SORT_ORDER_DESCENDING",
}
# BasicReportSourceType : 0 NONE / 1 CRITERIA / 2 SELECTION / 3 BROWSER
SRC_TYPE = {
    "NONE": "BASIC_RPT_SRC_TYPE_NONE",
    "CRITERIA": "BASIC_RPT_SRC_TYPE_CRITERIA",
    "SELECTION": "BASIC_RPT_SRC_TYPE_SELECTION",
    "BROWSER": "BASIC_RPT_SRC_TYPE_BROWSER",
}

_INT_FRACTION = re.compile(r"^-?\d+\.0+$")  # 11.000000, -1.000000 — PAS les dates 2010.01.25


def _text(node, tag, default=""):
    if node is None:
        return default
    child = node.find(tag)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def _norm_num_str(value):
    """11.000000 -> "11" ; -1.000000 -> "-1" ; laisse le reste (dates, textes) intact."""
    return str(int(float(value))) if _INT_FRACTION.match(value) else value


def _to_number(value, default=0):
    """Filter / champs numériques du JSON : renvoie int si entier, sinon float."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return int(f) if f.is_integer() else f


def _to_bool(value):
    return str(value).strip() == "1"


def _norm_param_name(name):
    """*Hided*PARAM_X -> *H*PARAM_X. *H* / *T* déjà canoniques -> inchangés."""
    if name.startswith("*Hided*"):
        return "*H*" + name[len("*Hided*"):]
    return name


def _convert_params(param_list_node):
    """ParamList XML -> tableau JSON [{name,value}].

    - éclate les valeurs pipe-délimitées (a|b|c) en entrées séparées, ordre préservé
    - ne touche JAMAIS aux séparateurs internes ':' '-' '.'
    - normalise les décimaux entiers (11.000000 -> 11)
    """
    out = []
    if param_list_node is None:
        return out
    for param in param_list_node.findall("Param"):
        raw_name = _text(param, "Name")
        if not raw_name:
            continue
        name = _norm_param_name(raw_name)
        raw_value = param.find("Value")
        value = "" if raw_value is None or raw_value.text is None else raw_value.text.strip()
        segments = value.split("|") if "|" in value else [value]
        for seg in segments:
            out.append({"name": name, "value": _norm_num_str(seg)})
    return out


def _convert_source(source_node):
    """<Source> Conseiller -> {sourceType, selections[], browsers[]}.

    Détecte le type par le sous-élément peuplé : Selections -> SELECTION,
    Criteria -> CRITERIA, Browser -> BROWSER, sinon NONE.
    """
    result = {"sourceType": SRC_TYPE["NONE"], "selections": [], "browsers": [{}]}
    if source_node is None:
        return result

    selections = source_node.find("Selections")
    field_name = _text(selections, "FieldName") if selections is not None else ""
    values = []
    if selections is not None:
        sel_list = selections.find("SelectionList")
        if sel_list is not None:
            values = [v.text.strip() for v in sel_list.findall("Value") if v.text and v.text.strip()]

    criteria = _text(source_node, "Criteria")

    browser = source_node.find("Browser")
    browser_records = []
    if browser is not None:
        rec_list = browser.find("RecordList")
        if rec_list is not None:
            browser_records = [v for v in rec_list if (v.text or "").strip()]

    if values:
        result["sourceType"] = SRC_TYPE["SELECTION"]
        result["selections"] = [{"fieldName": field_name, "values": values}]
    elif criteria:
        result["sourceType"] = SRC_TYPE["CRITERIA"]
    elif browser_records:
        result["sourceType"] = SRC_TYPE["BROWSER"]
    return result


def convert(xml_text, session_id="", session_token="", batch_name="ReportBatchService"):
    root = ET.fromstring(xml_text)

    # --- StandardReports : le JSON ne garde que rptJoinId + params ---
    standard_reports = []
    for sr in root.findall("./StandardReportList/StandardReport"):
        standard_reports.append({
            "rptJoinId": _to_number(_text(sr, "RptJoinId"), 0),
            "params": _convert_params(sr.find("ParamList")),
        })

    common = root.find("CommonBasicReportInfo")
    gen_order = common.find("GenerationOrder") if common is not None else None

    common_report_info = {
        "startPageFrom": _to_number(_text(common, "StartPageFrom", "1"), 1),
        "pdfTotPage": _to_number(_text(common, "NbPDFTotPage", "-1"), -1),
        "generationOrder": {
            "fieldToSort": _text(gen_order, "FieldToSort"),
            "sortOrder": SORT_ORDER.get(_text(gen_order, "OrderToSort", "1"), SORT_ORDER["1"]),
        },
        "currency": _text(common, "Currency", "DEFAULT"),
        "language": _text(common, "Language", "DEFAULT"),
        "userTitle": _text(common, "UserTitle"),
        "username": _text(common, "UserName"),
        "filter": _to_number(_text(common, "Filter", "-1"), -1),
        "addUserName": _to_bool(_text(common, "AddUserName", "0")),
        "groupNode": _to_bool(_text(common, "GroupNode", "0")),
        "messageInfo": {},
        "source": _convert_source(common.find("Source") if common is not None else None),
    }

    result = {
        "name": batch_name,
        "priority": _to_number(_text(root, "Priority", "2"), 2),
        "standardReports": standard_reports,
        "commonReportInfo": common_report_info,
        "brokersDiary": {},
        "ordersEntry": {},
        "generationOutput": GENERATION_OUTPUT.get(_text(root, "GenerationOutput", "1"), GENERATION_OUTPUT["1"]),
        "resultFileFormat": RESULT_FILE_FORMAT.get(_text(root, "ResultFormat", "1"), RESULT_FILE_FORMAT["1"]),
        "sessionId": session_id,
        "sessionToken": session_token,
    }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Conseiller TaskSpec XML -> Xpert generation JSON")
    parser.add_argument("input", help="fichier XML d'entrée (TaskSpec Conseiller)")
    parser.add_argument("-o", "--output", help="fichier JSON de sortie (défaut: stdout)")
    parser.add_argument("--session-id", default="", help="sessionId runtime (absent du XML)")
    parser.add_argument("--session-token", default="", help="sessionToken 'Bearer ...' (absent du XML)")
    parser.add_argument("--name", default="ReportBatchService", help="champ 'name' du batch")
    args = parser.parse_args(argv)

    with open(args.input, "r", encoding="ISO-8859-1") as f:
        xml_text = f.read()

    payload = convert(xml_text, args.session_id, args.session_token, args.name)

    if not args.session_id or not args.session_token:
        sys.stderr.write(
            "AVERTISSEMENT: sessionId/sessionToken absents du XML (jetons runtime). "
            "Renseigne-les via --session-id / --session-token avant d'envoyer la requête a l'API.\n"
        )

    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()
