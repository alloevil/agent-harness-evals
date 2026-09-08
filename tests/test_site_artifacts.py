"""Contract tests for the published retrieval artifacts.

The site, the JSON-LD, llms.txt, llms-full.txt and claims.json are all rendered from one payload.
These tests pin the property that makes them trustworthy: every number in them is read off that
payload, never written by hand, and nothing points at a file the repository does not publish.
No parquet needed — the payload shape is the contract.
"""
import json
import xml.dom.minidom

import build_site as bs

PAYLOAD = {
    "updated": "2026-01-02",
    "totals": {"records": 1234, "benchmarks": 7, "models": 5, "harnesses": 9},
    "benchmarks": {
        "wide": {
            "name": "Wide Bench", "blurb": "does things", "link": "https://example.invalid/wide",
            "harnesses": ["a", "b", "c"], "models": ["m1", "m2"],
            "summary": {"bestCombo": ["m1", "a", 0.9], "bestHarness": ["a", 0.98, 2],
                        "medianSpread": 0.111, "spreadModels": 4},
        },
        "thin": {
            "name": "Thin Bench", "blurb": "", "link": "",
            "harnesses": ["a", "b"], "models": ["m1"],
            "summary": {"bestCombo": ["m1", "a", 0.5], "bestHarness": None,
                        "medianSpread": None, "spreadModels": 0},
        },
        "native": {
            "name": "Native Bench", "blurb": "vendor CLIs", "link": "",
            "native": True, "harnesses": ["cli-x", "cli-y"], "models": ["m1", "m2"],
            "summary": {"bestCombo": ["m1", "cli-x", 0.7]},
        },
    },
}


def test_json_ld_is_a_valid_dataset_document():
    doc = json.loads(bs.json_ld(PAYLOAD))
    assert doc["@type"] == "Dataset"
    assert doc["url"] == f"{bs.SITE}/"
    assert doc["dateModified"] == PAYLOAD["updated"]
    # counts are quoted from the payload, so the description cannot claim a size the data denies
    assert "1234" in doc["description"] and "7 benchmarks" in doc["description"]
    for name in ("Wide Bench", "Thin Bench", "Native Bench"):
        assert name in doc["keywords"]


def test_json_ld_never_advertises_an_unpublished_download():
    doc = json.loads(bs.json_ld(PAYLOAD))
    for dist in doc.get("distribution", []):
        rel = dist["contentUrl"].removeprefix(f"{bs.SITE}/")
        assert (bs.DOCS / rel).exists(), f"DataDownload points at unpublished {rel}"


def test_page_renders_every_placeholder():
    html = (bs.TEMPLATE.replace("__JSONLD__", bs.json_ld(PAYLOAD))
            .replace("__DATA__", json.dumps(PAYLOAD, separators=(",", ":"))))
    assert "__JSONLD__" not in html and "__DATA__" not in html


def test_claims_are_derived_from_the_payload():
    doc = bs.claims(PAYLOAD)
    assert doc["updated"] == PAYLOAD["updated"]
    keys = {"id", "claim", "value", "metric", "method", "repro", "evidence", "verified"}
    for item in doc["claims"]:
        assert set(item) == keys and all(item[k] for k in keys)
        assert "no evaluation is run by this project" in item["method"]
    by_id = {item["id"]: item for item in doc["claims"]}
    assert by_id["records-reconciled"]["value"] == "1234"
    assert by_id["median-harness-spread-wide"]["value"] == "0.111"
    assert "4 models" in by_id["median-harness-spread-wide"]["claim"]
    # a board where no model has 3+ harnesses has no spread to claim, and a native board has no matrix
    assert "median-harness-spread-thin" not in by_id
    assert "median-harness-spread-native" not in by_id


def test_llms_files_quote_the_payload_and_stay_self_contained():
    short, full = bs.llms_txt(PAYLOAD), bs.llms_full_txt(PAYLOAD)
    for text in (short, full):
        assert text.startswith("# agent-harness-evals")
        assert PAYLOAD["updated"] in text and "1234" in text
        assert "runs no evaluations" in text or "runs no models" in text
    for name in ("Wide Bench", "Thin Bench", "Native Bench"):
        assert name in short
    for heading in ("## What it is", "## Install", "## Quickstart", "## Verifiable claims",
                    "## When to use it", "## When NOT to use it", "## FAQ"):
        assert f"\n{heading}\n" in full
    assert "Thin Bench" in full  # named as a board with no publishable spread


def test_sitemap_lists_every_published_page_and_parses():
    dom = xml.dom.minidom.parseString(bs.sitemap_xml())
    locs = {node.firstChild.data for node in dom.getElementsByTagName("loc")}
    published = {f"{bs.SITE}/"} | {f"{bs.SITE}/{p.name}" for p in bs.DOCS.glob("*.html")
                                   if p.name != "index.html"}
    assert locs == published


def test_robots_points_at_the_sitemap():
    assert bs.robots_txt() == f"User-agent: *\nAllow: /\n\nSitemap: {bs.SITE}/sitemap.xml\n"



def test_robots_points_at_the_sitemap():
    assert bs.robots_txt() == f"User-agent: *\nAllow: /\n\nSitemap: {bs.SITE}/sitemap.xml\n"
