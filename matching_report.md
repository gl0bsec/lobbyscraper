# EU Transparency Register Matching — Statistical Report

## Overview

This report documents the process, outcomes, and iterative refinements of matching feedback respondents from the EU Digital Omnibus consultation (374 documents) to entries in the EU Transparency Register.

Total dataset: 374 rows. Each row represents one feedback document; organisation names were taken from the portal submission metadata.

---

## Final Match Outcomes

| Status | Count | Share |
|---|---:|---:|
| Matched | 258 | 69.0% |
| Unmatched | 116 | 31.0% |
| — of which: unmatched with org name | 88 | 23.5% |
| — of which: confirmed non-registrants | 2 | 0.5% |
| — of which: no org name (individuals) | 26 | 7.0% |

---

## Match Type Breakdown

All 258 matched rows, by the method that produced the match:

| Match Type | Count | Share of total |
|---|---:|---:|
| `exact` | 107 | 28.6% |
| `normalized` | 76 | 20.3% |
| `starts_with` | 28 | 7.5% |
| `fuzzy` | 29 | 7.8% |
| `manual_exact` | 13 | 3.5% |
| `cross_country` | 4 | 1.1% |
| `manual_normalized` | 1 | 0.3% |
| `no_match` | 114 | 30.5% |
| `no_match_verified` | 2 | 0.5% |

---

## Confidence Score Distribution

Among the 258 matched rows (minimum threshold: 0.85):

| Confidence | Count | Share of matched |
|---|---:|---:|
| 1.000 (exact / normalized) | 196 | 76.0% |
| 0.950 (starts_with / confirmed fuzzy) | 38 | 14.7% |
| 0.900–0.949 (fuzzy) | 15 | 5.8% |
| 0.850–0.899 (fuzzy / cross-entity) | 9 | 3.5% |

Mean confidence: **0.984** | Median: **1.000** | Minimum: **0.850**

No matched row falls below the 0.85 threshold.

---

## Matched Organisation Categories

Category breakdown of the 258 matched rows, as declared in the Transparency Register:

| Category | Count | Share of matched |
|---|---:|---:|
| Trade and business associations | 122 | 47.3% |
| Companies & groups | 78 | 30.2% |
| Non-governmental organisations, platforms and networks | 33 | 12.8% |
| Trade unions and professional associations | 11 | 4.3% |
| Other organisations, public or mixed entities | 7 | 2.7% |
| Associations and networks of public authorities | 4 | 1.6% |
| Think tanks and research institutions | 3 | 1.2% |

---

## Unmatched Respondents — Profile

### By declared user type

| User Type | Unmatched (w/ org) | Share |
|---|---:|---:|
| COMPANY | 27 | 30.7% |
| BUSINESS_ASSOCIATION | 25 | 28.4% |
| ACADEMIC_RESEARCH_INSTITTUTION | 11 | 12.5% |
| PUBLIC_AUTHORITY | 9 | 10.2% |
| NGO | 7 | 8.0% |
| OTHER | 7 | 8.0% |
| CONSUMER_ORGANISATION | 1 | 1.1% |
| TRADE_UNION | 1 | 1.1% |

### By country (top 10)

| Country | Count |
|---|---:|
| DEU | 11 |
| FRA | 9 |
| ITA | 8 |
| NLD | 8 |
| BEL | 7 |
| GBR | 6 |
| USA | 6 |
| ESP | 5 |
| CZE | 4 |
| DNK | 3 |

### Reasons for remaining non-match

| Reason | Approx. count |
|---|---:|
| Not registered (SMEs, startups, small nationals) | ~45 |
| Government / public body (not required to register) | ~12 |
| Academic / research institution | ~12 |
| Registered but absent from local register file (e.g. ENTSO-E, BVMed, eyeo) | ~4 |
| Non-EU organisations with no EU registration | ~6 |
| Ambiguous / collective submissions | ~9 |

---

## Review Flags

All flagged rows are resolved — flags serve as an audit trail:

| Flag | Count | Meaning |
|---|---:|---|
| `RETROACTIVE_MATCH` | 50 | New match added during post-hoc review |
| `FALSE_POSITIVE_CORRECTED` | 26 | Previously matched incorrectly; corrected to no_match |
| `FUZZY_LIKELY_CORRECT` | 18 | Fuzzy match reviewed and accepted (original pipeline) |
| `MANUAL_MATCH_VERIFIED` | 14 | Manual match confirmed correct (original pipeline) |
| `CROSS_COUNTRY_LIKELY_CORRECT` | 3 | Cross-country match accepted |
| `FALSE_POSITIVE_VERIFIED` | 1 | Match rejected, confirmed false positive |
| `VERIFIED_CORRECT` | 1 | Extra verification of a correct match |
| `DIFFERENT_ENTITY_VERIFIED` | 1 | Confirmed different entity; no match |

---

## Process Refinement

The matching pipeline went through three distinct phases of review and correction.

### Phase 0 — Baseline (original automated pipeline)

The initial pipeline ran five strategies in sequence — exact, normalised, fuzzy (≥ 0.85), starts-with, and cross-country fallback — against the EU Transparency Register file (12,771 entries). A manual review pass then added `manual_exact` and `manual_normalized` matches. This produced:

| | |
|---|---:|
| Matched | 234 (62.6%) |
| Unmatched | 140 (37.4%) |
| Review flags set | 64 |

### Phase 1 — False positive correction (−26 matches)

Inspection revealed that 26 rows with no `organization` value had been bulk-assigned to *Computer and Communications Industry Association* (CCIA, ID `281864052407-46`) during the manual review pass. The affected rows were all individual EU/non-EU citizen submissions (confirmed via web research: Sebastian Felix Schwemer — law professor at BI Norwegian Business School; Robin Berjon — IPFS Foundation; Rigo Wenning — W3C Legal Counsel; and others). None of the 26 documents contained a reference to CCIA.

All 26 were corrected to `no_match` and flagged `FALSE_POSITIVE_CORRECTED`. The match rate fell to **55.6%** on a now-accurate basis.

### Phase 2 — Algorithm gap recovery (+21 matches)

The original fuzzy algorithm used a tight string-length pre-filter (`abs(len) > 30` chars difference) and a 0.85 similarity threshold, which caused it to miss:

- Organisations where the feedback submission used a long descriptive name but the register entry used only the acronym (e.g. *CECIMO — European Association of Manufacturing Technologies* → *CECIMO*)
- The reverse: short acronym in submission, full name in register (e.g. *CLEPA* → *European Association Automotive Suppliers*)
- Known name changes or rebranding (e.g. *Connect Europe*, the rebranded ETNO)
- Organisations registered under a different language variant (e.g. *Volkswagen Group* → *Volkswagen Aktiengesellschaft*)
- Abbreviation-style submissions (e.g. *AFME*, *LSEG*, *CPME*, *ASNEF*)

Web searches confirmed 7 additional matches with IDs not surfaced by the algorithm (CLEPA, AFME, Volkswagen Group, VDMA, CPME, ASNEF, LSEG). Combined with 14 confirmed algorithm candidates, **21 new matches** were applied. Match rate rose to **61.2%**.

### Phase 3 — Exhaustive sweep (+24 + 5 matches)

A systematic pass through all 117 remaining unmatched organisations with org names was conducted, combining:

1. Targeted fuzzy search against the register file (lower length-filter, same 0.82 threshold for candidates, manually reviewed)
2. Web searches on organisations likely to be registered but using substantially different official names

This identified a further 29 matches in two sub-passes. Key patterns recovered:

- National-language register names vs. English submission names (e.g. *ALFI* → *Association Luxembourgeoise des Fonds d'Investissement*; *WKÖ* → *Wirtschaftskammer Österreich*; *vzbv* → *Verbraucherzentrale Bundesverband*)
- Rebranded organisations (e.g. *FEDMA* → *Federation of European Data and Marketing*; *TEAM-NB* → *The European Association of Medical Devices – Notified Bodies*)
- Subsidiary / operating-entity matches (e.g. *Ingka Group IKEA* → *Ingka Services A.B.*; *Elia Group* → *Elia Transmission Belgium*)
- Joint submissions listed under a combined name (e.g. *EMMA-ENPA* matched to *European Magazine Media Association*)

**8 false positive candidates** from the algorithm were explicitly rejected: NCC Group → CEC Group, D-Trust → Dogs Trust, Elia Group → CELSA Group, ESYS Foundation → Wemos Foundation, Global Data Alliance → Global Battery Alliance, Connect Europe → NEC Europe, U.S. Chamber of Commerce → The Danish Chamber of Commerce, Digital Poland Association → Digital Lending Association.

Final match rate: **69.0%** (258 / 374).

---

## Cumulative Match Rate Progression

| Phase | Matched | Rate | Change |
|---|---:|---:|---:|
| Baseline (original pipeline) | 234 | 62.6% | — |
| After Phase 1 (false positive correction) | 208 | 55.6% | −26 |
| After Phase 2 (algorithm gap recovery) | 229 | 61.2% | +21 |
| After Phase 3a (exhaustive sweep) | 253 | 67.6% | +24 |
| After Phase 3b (final sweep) | **258** | **69.0%** | +5 |

---

## Script Improvements Applied

Following this review, `eu_lobbyscraper/match_organizations.py` was updated with four changes. Zero regressions on the existing matched dataset were introduced; 38 of the 50 retroactive matches are still only reachable via human lookup (cross-language cases).

### 1. Unicode/ASCII folding in `normalize_org_name`

```python
name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
```

Applied after lowercasing. Strips all diacritics so `Österreich == Osterreich`, `Yrittäjät == Yrittajat`, `Economía == Economia`. Without this, accented characters caused exact and normalised strategies to silently fail.

### 2. Additional legal suffixes

Added `ry` (Finnish registered association), `aisbl` (Belgian international non-profit), `se` (Societas Europaea), `eeig` (European Economic Interest Grouping) to the suffix stripping list.

### 3. Reverse starts-with in Strategy 4

The original only checked: *does the register entry start with the submission name?* (e.g. `"GSMA"` → `"GSMA Europe"`). The reverse direction — *does the submission start with the register entry?* — was not checked, missing cases where respondents appended a description or national qualifier to the official short name:

| Submission | Register entry |
|---|---|
| Nordic Financial Unions - the Nordic financial trade unions confederation | Nordic Financial Unions |
| Bundesverband der Deutschen Industrie (BDI) / Federation of German Industries | Bundesverband der Deutschen Industrie e.V. |
| Zentralverband des Deutschen Handwerks (ZDH) - Europaabteilung Brüssel | Zentralverband des Deutschen Handwerks e.V. |
| RECHARGE - The Advanced Rechargeable & Lithium Batteries Association | RECHARGE aisbl |
| CECIMO - European Association of Manufacturing Technologies | CECIMO |
| Renault Group | RENAULT |
| Prosus Group | Prosus |

### 4. Expanded Strategy 5 (cross-country fallback)

Previously Strategy 5 only attempted exact-normalised and forward starts-with across non-home countries. It now also:

- Checks starts-with in **both directions** cross-country (min 6 chars each side)
- Runs a **global fuzzy pass** (threshold floored at 0.88 — higher than the within-country default of 0.85 — with a 25-char length pre-filter for speed)

This catches orgs registered under a different country code than the one declared in the submission, which is common for Brussels-based federations and US/UK-headquartered companies with EU registrations.

### What the script still cannot fix

38 retroactive matches from this exercise remain beyond algorithmic reach. All are **cross-language** cases where the submission uses an English name and the register entry uses the national language with no textual overlap:

| Example submission | Register entry | Language gap |
|---|---|---|
| German Insurance Association | Gesamtverband der Deutschen Versicherungswirtschaft e.V. | EN → DE |
| Federation of German Consumer Organisations (vzbv) | Verbraucherzentrale Bundesverband | EN → DE |
| Association of Netherlands Municipalities | Vereniging van Nederlandse Gemeenten | EN → NL |
| ALFI - Association of the Luxembourg Fund Industry | Association Luxembourgeoise des Fonds d'Investissement | EN → FR |
| Confederation of Industry of the Czech Republic | Svaz průmyslu a dopravy ČR | EN → CS |

Resolving these would require one of:

1. **A maintained alias dictionary** mapping English common names to register IDs — practical for frequently-recurring orgs
2. **Machine translation** of register names to English before indexing — adds noise, may help for long descriptive names
3. **Register ID pre-annotation** in the feedback collection step, if the portal provides it

---

## Notes on the Register File

The local `transparency_register.csv` (12,771 entries) appears to be a point-in-time export and is missing at least four organisations confirmed as currently registered:

| Organisation | Known ID | Notes |
|---|---|---|
| ENTSO-E | `02207557481-49` | EU network operators assoc |
| BVMed | `103122495301-83` | German medical tech assoc |
| eyeo GmbH | `723964794852-72` | Adblock Plus maker |
| EVOLIS | *(lobbyfacts entry exists)* | Card industry assoc |

Updating the register file to a more recent export would recover these 4 matches and likely others.
