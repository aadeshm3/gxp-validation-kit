# LCDA Phase 1 — Master Context File

> **Purpose:** Single source of truth to bootstrap a new Claude/Copilot session or recover after context-compaction. Drop this file into any new chat and the assistant will have full project context.

**Last refreshed:** 2026-06-23
**Author / user:** Aadesh Malviya — **Validation & Test Engineer**, Deloitte US Consulting (contracted to Eli Lilly)
**Working directory:** `C:\Users\L132245\OneDrive - Eli Lilly and Company\Desktop\LCDA Phase1`

**My role on LCDA:** I own the validation + test deliverables for LCDA Phase 1. That means: authoring & maintaining the URS / Functional Requirements, Validation Test Plan (VTP), test cases (Playwright API-mode for system testing, manual scripts for UAT), traceability matrix, test execution evidence, defect tracking, and the Validation Summary Report. I work with BSME (Wendy), TSME (Liping/David), CSQA (Mansi), BQA (Poh) and Security (Shawn/Tim/Ashutosh) to get artifacts reviewed and approved per LQP-302-25 / LQP-302-26. I also classify requirements (User vs Functional), prepare them for ALM upload, and shepherd Change Requests (e.g., CHG2851220) through ServiceNow per LCS-501.

---

## 1. Identity & user preferences

- User signs as **Aadesh Malviya**
- Concise replies preferred; no fluff
- Use markdown links for files (not backticks); never use emojis unless asked
- Occasional Hindi-English mix is fine
- ALM-clean wording for ACs (no vendor names, no "e.g.", no hedges)
- GxP-compliant phrasing in plans (no rigid bullet examples; use "e.g." inline if needed)
- Persist through blockers; do not ask permission for safe local actions; ask before destructive ops

---

## 2. Project — LCDA at a glance

**Full name:** Lilly Clinical Data Aggregation (LCDA) Platform
**Phase:** Phase 1 / MVP1
**Go-live target:** Phase 1 MVP in EDB Dev by **7/31/2026** (Path A — EDB infrastructure)
**System Risk Category:** **RC#4 (GxP)** per LQP-302-25 (RP0012937)
**Compliance frame:** 21 CFR Part 11, GAMP 5, ALCOA+
**Quality Workflow in CMDB:** **Validation** (Business Application CI)
**System type:** GxP Business Application, no UI (API-driven only)

**Mission (one line):** Aggregate Lilly clinical study data from authoritative source systems (Veeva CDB, LabsConnect) into a centralized Databricks Lakehouse for downstream analytics, with full audit/lineage/RBAC.

> **Scope note (2026-06-19):** eCTS has been confirmed OUT OF SCOPE for Phase 1. All eCTS references in VTP, DS, Requirements, and Confluence page need to be removed. eCTS to be addressed in a later phase.

### What LCDA actually does (plain English)
Lilly runs clinical trials. The data from those trials lives in many disconnected source systems — **Veeva CDB** (clinical database / EDC), **LabsConnect / LabConnect** (central lab results), **eCTS** (electronic Clinical Trial Supply), and others. Today, study teams, biostatisticians, and data scientists have to pull from each silo separately, reconcile formats, and re-do that work for every study. That is slow, error-prone, and breaks GxP traceability.

**LCDA** (Lilly Clinical Data Aggregation Platform) solves this by being the **single, governed, GxP-validated landing + conformance layer** for clinical study data:

1. **Ingest** — Scheduled Databricks Jobs pull data from each authoritative source (API, SFTP, or file drop) into S3 **Landing**.
2. **Raw** — Auto-loader lands raw, immutable copies in S3 + Delta tables (Bronze).
3. **Refined / Conformed** — Schema validation, data-quality checks, and standardization to a common clinical model (Silver).
4. **Consume** — Downstream analytics, statistical programming, dashboards, and ML/AI use cases query LCDA via Databricks SQL Warehouse + Unity Catalog (Gold).
5. **Govern** — Unity Catalog provides lineage, RBAC, masking, and audit; Delta Time Travel + Deep Clone provide GxP-grade recoverability; ALCOA+ and 21 CFR Part 11 controls are applied throughout.

**Phase 1 / MVP1 scope:** Stand up the platform on EDB Databricks Dev → QA → Prod, onboard the first source (Veeva CDB extraction job is already in the repo), and prove the end-to-end pattern with full validation deliverables (VTP, requirements, DS, test execution, SVR). No UI is in scope — LCDA is API/data-platform only.

**Out of scope (Phase 1):** Agentic / AI-ML workloads, additional sources beyond the agreed initial set, independent (Path B) Databricks workspace.

---

## 3. Stakeholders / RACI

| Person | Role | Group |
|---|---|---|
| **Aadesh Malviya** | Validation & Test Engineer | VAL (Deloitte) |
| **Wendy Huber** | BSME (Business SME) | Business |
| **Liping Cai** | TSME (Technical SME) | Engineering |
| **David Cantrell** | TSME (Technical SME) | Engineering |
| **Sharon M Klein** | System Owner (SO) | Lilly |
| **Carrie Wertz** | System Custodian (SC) | Lilly |
| **Mansi Agarwal** | CSQA | Quality |
| **Poh Chiam Sim** | BQA | Quality |
| **Shawn / Tim** | BISO | Security |

**Canonical reviewer GROUPS (used in exec view):**
`VAL + BSME` · `TSME, BSME, SO, SC` · `TSME` · `CSQA` · `BISO` · `BQA & CSQA`

---

## 4. Architecture (current — post CR CHG2851220)

### Decision history
- Original plan considered AWS-native (Lambda + API Gateway + Step Functions + MWAA/Airflow + MCP) → rejected
- **Final approved path (Path A from deck slide 4):** Start on **EDB Databricks** Dev (NON-HIPAA), promote to EDB QA + EDB Prod (HIPAA). Long-term Path B (independent LCDA Databricks) deferred.
- **CR CHG2851220** approved this Databricks-centric architecture pivot.

### Tech stack — RETAINED
- **Databricks** workspace `dbc-f887d59d-e4c5.cloud.databricks.com` (EDB)
- Databricks Jobs (orchestration — replaces Airflow/MWAA)
- Unity Catalog (governance, lineage, RBAC, masking via UDFs)
- Databricks SQL Warehouse API (consumption — replaces API Gateway/Lambda)
- Delta Lake — Time Travel + Deep Clone (backup/recovery)
- AWS S3 (Landing / Raw / Conformed) with versioning + cross-region replication
- AWS IAM, AWS KMS
- AWS Secrets Manager
- GitHub Enterprise (`Deloitte-US-Consulting/lly-lcda-dbx`) + GitHub Actions for CI/CD
- Databricks Asset Bundles (DAB) for deployment
- Playwright (API mode via `request` context only — NO UI in LCDA)
- Checkmarx (SAST)
- Wiz (cloud vuln scan)
- ServiceNow (incident + change mgmt)

### Tech stack — REMOVED
- AWS MWAA / Airflow
- AWS Lambda
- AWS API Gateway
- AWS Step Functions
- MCP

### Data flow (deck slide 33 — Solution Architecture MVP1)
```
Veeva CDB (full, S3 file)
LabsConnect    (full, S3 file)   ──►  S3 Landing  ──►  Schema Validation (DBX job)
eCTS Oracle    (JDBC incremental)                          │ fail → ServiceNow incident
                                                           ▼
                                                  Raw Delta (bronze, schema enforced)
                                                           │ SCD Type-2 + harmonization
                                                           ▼
                                                  Refined Delta (silver, master schema per form)
                                                           │ SDTM mapping, USUBJID format
                                                           ▼
                                                  Conform Delta (gold)
                                                           │
                                                  Consumption:
                                                    – Databricks SQL Warehouse API (REST)
                                                    – JDBC via SQL Warehouse
                                                    – Delta Sharing
                                                    – DIVA integration (Power BI via pre-signed S3 URLs)
```

### Layer / catalog naming (confirmed from deck slide 47 + slide 12)

**Unity Catalog names (top-level):**
- `lly_lcda_raw_dev` — Raw catalog (schema enforced)
- `lly_lcda_refined_dev` — Refined catalog (schema enforced)
- `lly_lcda_conform_dev` — Conform catalog (schema enforced + SCD)

**Source-specific landing catalogs:**
- CDB landing: `lrl_raw_lcda_cdb_dev` — S3: `s3://lly-lcda-cdb-dev/__unitystorage/`
- LabsConnect landing: `lrl_raw_lcda_labs_dev` — S3: `s3://lly-lcda-labs-dev/__unitystorage/`
- ECTS landing: `lrl_raw_lcda_ects_dev` — S3: `s3://lly-lcda-ects-dev/__unitystorage/`
- Common refined store (all sources): `lrl_refined_lcda_dev`

**S3 bucket paths:**
- Landing zone: `s3://lly-lcda-landing-dev` (subfolders: `/input`, `/archive`)
- Raw: `s3://lly-lcda-raw-dev/__unitystorage/`
- Refined: `s3://lly-lcda-refined-dev/__unitystorage/`

**Schema names per layer per source:**

| Source | Landing schema | Raw schema | Refined schema |
|---|---|---|---|
| Veeva CDB (EDC) | `lnd_cdb_edc` | `raw_cdb_edc` | `refined_cdb_edc` |
| Veeva CDB (eCOA) | `lnd_cdb_ecoa` | `raw_cdb_ecoa` | `refined_cdb_ecoa` |
| Veeva CDB (Grants) | `lnd_cdb_grants` | `raw_cdb_grants` | `refined_cdb_grants` |
| LabsConnect | `lnd_labsconnect` | `raw_labsconnect` | `refined_labsconnect` |
| ECTS | — (zero-copy Oracle) | `raw_ects` | **No refined layer (by design)** |

**Table counts (confirmed):**
- CDB: ~75 files/tables per study, ~100 studies → Raw: 1 table per file per study; Refined: 80 form-level master tables (harmonized across studies)
- LabsConnect: 4 files per study (LB, IG, PK, ECG) → Raw: 4 tables; Refined: 4 form tables
- ECTS: 19 RTSM tables → Raw: 19 tables; Refined: none

**Delta lake internal schema structure (lly_lcda_raw_dev):**
- `cdb_edc`: DM1001, AE3001, LB, VS, ... (~60 form tables)
- `cdb_ecoa` (~14 form tables)
- `cdb_grants` (~1 form table)
- `ects`: 19 tables (ctsald_owner_ref.*, aladdin_ref.*)
- `labsconnect`: LB, IG, PK, ECG

### ETL pipeline — per-source steps (confirmed from slides 15–17)

**Veeva CDB (Source 1 of 3):**
1. STEP 0: Immutable ZIP files pulled from FTP/S3 source; file naming pattern: `J1I-MC-GZQB_EDC_LCDA.zip`; inside: form-wise CSV + manifest file
2. STEP 1: Unzip study-wise ZIP (Export folders only — eCoA, EDC, Grants); stored in Databricks volume
3. STEP 2: Schema Validation via Python notebook against manifest file
   - Success → Autoloader loads into landing (`lnd_cdb_grants/ecoa/edc`); ZIP archived
   - Fail → file moved to error volume (`schema: CDB, volume: Volume/error`)
4. STEP 3 (Raw): Full Truncate & Load at study level; format: Delta table; partitioned by Study ID
5. STEP 4 (Refined): SCD Type 2 incremental; harmonized master schema per form across studies; format: Delta table

**LabsConnect (Source 2 of 3):**
1. STEP 0: Immutable sas7bdat files pulled from source via connector
2. STEP 1: Convert sas7bdat → CSV (browse studies → subfolders; e.g., study `111-CT-WIN2`, subfolders: pk, ecg)
3. STEP 2: Schema Validation against fixed DDL
   - Success → Autoloader into `lnd_labsconnect`; archive study-level folder
   - Fail → error volume (`schema: lnd_labsconnect, volume: Volume/error`)
4. STEP 3 (Raw): Full Truncate & Load at study level; partitioned by Study ID; schema: `raw_labsconnect`
5. STEP 4 (Refined): SCD Type 2 incremental; schema: `refined_labsconnect`

**ECTS (Source 3 of 3):**
1. STEP 0: Federated connector (zero copy) — Databricks directly connects to Oracle ECTS DB
2. STEP 1: Connect to 19 RTSM tables from ECTS Oracle DB; no file conversion needed
3. STEP 2: Schema Validation against fixed DDL
   - Success → SCD Type 2 loads directly from Oracle zero-copy source into `raw_ects`
   - Fail → error thrown on schema validation
4. STEP 3 (Raw): Incremental SCD Type 2 at study level; schema: `raw_ects`; each table has Study ID, Subject ID, last update timestamp
5. **No refined layer** — by design per client guidance

**ECTS RTSM source table mapping (slide 45):**
| RTSM table | Oracle source tables |
|---|---|
| RTSM_RANDOMIZATION | cdts_owner.dtp_sms_randomization_f, cdts_owner.dtp_sms_treatment_group_ref |
| RTSM_SBJCT_DATA | ctsald_owner_ref.cts_research_project, cts_study, cts_study_parms, aladdin_ref.authsites, aladdin_ref.authusers, cts_authuser_parms, cts_person_authuser, cts_person, cts_subject, cts_subject_contact, cts_randomization, cts_subj_status_ref, cts_sch_contact, cts_unsch_cntct, cts_subj_cntct_parms, cts_parm_value, cts_dc_control, cts_parm_type_ref, cts_subject_parms |
| RTSM_TREATMENT_DISPENSE | cdts_owner.dtp_sms_treatment_dispense_f |

### Orchestration — job schedule (confirmed from slide 32)

| Job name | Schedule | Layer |
|---|---|---|
| `LCDA_ETL_CDB_Daily_Job` | Daily | Raw |
| `LCDA_Source_Data_Load_LabsConnect_Daily_Job` | Daily, 4:00 AM ET | Raw |
| `LCDA_Source_Data_Load_ECTS_Job` | Daily, 9:45 AM ET | Raw |
| `LCDA_Data_Transformation_CDB_Job` | — | Raw → Refined |
| `LCDA_Data_Transformation_Labsconnect_Job` | — | Raw → Refined |
| `LCDA_Data_Transformation_ECTS_Job` | — | (Raw only — no refined) |

Orchestration uses Databricks Workflows (DAG tasks). Config/STTM YML files managed in GitHub, deployed via DAB + GitHub Actions.

### Audit / log tables (confirmed table locations and full schema)

**`raw_catalog.etl_control.job_run_log`** (AuditControlTable — one row per end-to-end job run):
| Column | Description | Sample |
|---|---|---|
| Job_id | Job Run ID | 924580894536643 |
| ppln_nm | Job name | LCDA_EXTRACTION_JOB |
| lst_run_ts | Job start timestamp (UTC) | 2025-08-14 22:30:00 |
| sts | Status | RUNNING / SUCCESS / FAILED |
| Tbl_nm | Target table name | AE3001 |
| Schm_nm | Target schema name | Cdb |
| Src_system | Source system | EPH |
| jb_end_ts | Job end timestamp (UTC) | — |
| run_nts | Run notes | — |
| src_count | Total source records | 301 |
| tgt_count | Total target records written | 301 |
| reject_count | Total rejected records | 0 |
| files_transferred | Total files transferred | 1 |
| merge_query / Insert_query / ddl_query | DDL executed | — |
| notebook_run_id | Databricks job run ID | 1080580369402168 |
| crtd_at / updt_at | Record created / updated timestamp | — |

**`raw_catalog.etl_control.pipeline_audit_log`** (LogTable — step-level detail):
| Column | Description |
|---|---|
| audit_id | Unique ID for log entry |
| job_id | Job ID (FK to job_run_log) |
| pipeline | Pipeline name (e.g., cdb_autoloader) |
| step | Step identifier |
| src_system | Source system (e.g., CDB) |
| status | Running / SUCCESS / FAILED |
| level | INFO / WARN / ERROR |
| message | Log message |
| step_ts | Step event timestamp (UTC) |
| rows_in / rows_out / rows_rejected / records_written | Row counts |
| files_transferred | Files transferred in step |
| dq_triage | Data quality triage info (JSON) |
| table_name | Target table (e.g., raw_catalog.cdb._ae3001_external) |
| s3_uris / file_paths | S3 paths and file paths processed |
| error_message / error_stack_trace | Error details |
| details | Additional JSON details |
| notebook_run_id | Databricks job run ID |

**Audit trace queries (from slide 30):**
```sql
-- Step 1: find job run
SELECT * FROM raw_catalog.etl_control.job_run_log ORDER BY lst_run_ts DESC;

-- Step 2: drill into step-level detail for a specific job_id
SELECT * FROM raw_catalog.etl_control.pipeline_audit_log
WHERE job_id = '<job_id>' ORDER BY step_ts DESC;
```

### Failure / retry
- 3 failure scenarios: pre-MERGE / mid-MERGE / mid-INSERT — all auto-rollback by Databricks; support team performs **repair-run** from point of failure; UPSERT pattern prevents duplicates.
- File failure path: Success → archive folder; Failure → error volume (file copied to archive, original left for investigation)
- Job can be manually restarted from point of failure by Ops Team / Databricks support team

### Data masking (RBAC)
- Unity Catalog UDF `anon_mask_udf` applied to columns at DDL level: `CREATE TABLE ... (frst_nm STRING MASK anon_mask_udf, ...)`
- Masking logic: `RETURN CASE WHEN is_account_group_member('priv_access_group') THEN identifier ELSE '*******' END;`
- `priv_access_group` — sees clear text data
- `bi_access_group` — sees `*******` masked values
- Service accounts for ETL retain clear-text across all 3 layers
- Databricks user roles: Business analyst group (read-only to Refined), Developer group (read-write for interactive queries)
- Access via SQL Warehouse API + SSO / Databricks SSO login

### Open development items (from slides 18–21, as of 2026-06-05)

| # | Source | Category | Issue | Owner | ETA | Status |
|---|---|---|---|---|---|---|
| 1 | LabsConnect | SCD Type II | Primary keys for SCD Type 2 in refined layer — initial suggestion: study_id, subject_id, last_updated_timestamp; no unique row identifier confirmed | Saswat / Nicholas | 2026-06-12 | Open |
| 2 | LabsConnect | File structure | Header structure confirmation at study level; incorrect lab data received (ECG, IG, PV showing lab data); incremental dataset needed | Saswat / Nicholas | 2026-06-09 | Open |
| 3 | LabsConnect | Incorrect data | Latest data to be shared by Sabyasachi | Sabyasachi | 2026-06-09 | Open |
| 4 | eCTS | Incremental load | No timestamp column present to identify changed records — incremental strategy TBD | Nancy / David | 2026-06-10 | Open |
| 5 | eCTS | SCD Type II | Primary keys for SCD Type 2 — initial: study_id, subject_id, last_updated_timestamp | Nancy / David | 2026-06-12 | Open |
| 6 | eCTS | Service Account | Service account credentials for ECTS needed; workaround: bring data from CDB Import folder (3 RTSM tables); test data exists in ECTS Dev (synthetic + non-red DB) | Nancy / David | 2026-06-09 | Open |
| 7 | CDB | Connectivity | FTP server Export folder — is structure constant or can it have timestamped subfolders? | Nancy / David | 2026-06-09 | Open |
| 8 | CDB | Connectivity | How to identify if data has been refreshed? | Nancy / David | 2026-06-11 | Open |
| 9 | CDB | SCD Type II | Primary keys for SCD Type 2 in refined layer — same challenge as LabsConnect | Nancy / David | 2026-06-12 | Open |
| 10 | All sources | Access Management | Consumption access approach: Raw vs Refined? System-level roles per source (CDB / LabsConnect / ECTS)? Consumer (Kia) current consumption method? | Kia | 2026-06-12 | Open |
| 11 | CDB | Data | Veeva EDC data needed in Imports folder for data analysis | Nancy / David | 2026-06-12 | Open |
| 12 | CDB (Internal) | Access | Access to DED and Study Builder output from Dheeraj | Jisi | 2026-06-11 | Open |

---

## 5. Phase 1 scope (deck slide 4)

### IN scope
- Veeva CDB, eCTS, LabsConnect ingestion (full + incremental)
- Unity Catalog audit + lineage
- Path to onboard ALL studies (multi-study)
- Consumption via Delta Lake (JDBC + SQL Warehouse API)
- Validation SDLC documents ready for QA approval

### OUT of scope
- Agentic processes / AI features
- eCOA / EDC ingestion (beyond what's bundled inside CDB)
- Data transformations (study-level)
- Data quality checks (study-level)
- Hypercare / SAE approval
- HIPAA workspaces (EDB Dev is NON-HIPAA in Phase 1)

### Source system facts
| Source | Mechanism | Notes |
|---|---|---|
| Veeva CDB | S3 ZIP files (one ZIP per study, ZIPs contain CSV) | ~100 studies, ~70 files/study → ~7,000 raw tables. Files: EDC (~60), eCOA (~14), Grants (~1) per study |
| LabsConnect | S3 files | 1 study = 4 files, same structure |
| eCTS | Oracle JDBC (Federated connector), incremental | RTSM tables: RTSM_RANDOMIZATION, RTSM_SBJCT_DATA, RTSM_TREATMENT_DISPENSE — composed from many `ctsald_owner_ref.*` and `aladdin_ref.*` source tables (19 underlying) |

### Refined layer harmonization
- ~80 form-level master tables (union across all studies per form)
- Schema evolution auto-applied for new/changed columns

---

## 6. Validation deliverables — current state

### Reviewer groups & rounds
Two-round review pattern with author rework between rounds:
1. **Round 1** review by reviewer group → 2. Author **Rework** (Feedback Implementation) → 3. **Round 2 (Align)** review.

### Per-deliverable group routing
| Deliverable | Reviewers |
|---|---|
| Validation & Test Plan (VTP) | TSME/BSME/SO/SC + CSQA |
| Requirements (ALM) | VAL + BSME (continuous) |
| Design Specification (DS) | TSME |
| Coding Standards | TSME |
| System Overview & Configuration | TSME/BSME/SO/SC |
| Security Plan & Admin SOP | TSME/BSME/SO/SC + CSQA + BISO |
| System Admin & Support SOP | TSME |
| System Audit Trail Assessment | TSME/BSME/SO/SC + BQA & CSQA |

### Status snapshot
- **Validation Plan (LCDA_Validation_Plan_v1.0_draft.docx)** — Generated 2026-06-23 from `CSV TEMPLATE- Validation Plan.docx` via the validation workbench. Status: **Draft**. Location: `deliverables/in-progress/`. 14 [CONFIRM] items require resolution before routing. Reviewer group: TSME/BSME/SO/SC + CSQA. Generated by `scripts/gen_vp.py`. See DELIVERABLE_STATUS.md.
- **VTP (LCDA_VP_TP_v2.0.docx)** — Routed 2026-06-03 in QualityDocs via **Collaborative Authoring** workflow to: Carrie Wertz, Wendy Huber, Sharon Klein, David Cantrell, Liping Cai. Review deadline was **2026-06-08** (today). Awaiting comments.
  - **Two-phase review alignment (confirmed 2026-06-04 with Carrie Wertz):**
    - Phase 1 — Collaborative Authoring: above 5 reviewers add comments → Aadesh resolves
    - Phase 2 — Formal Review & Approval: re-route with ALL stakeholders including Mansi (CSQA) and Poh (BQA). Mansi confirmed she reviews after Phase 1 comments are addressed.
  - Workflow rationale: Review & Approval workflow forces Mansi + Poh into the same review window; Collaborative Authoring allows Phase 1 team to review first without triggering Mansi/Poh prematurely.
  - **Next action:** Collect Phase 1 comments by 08-Jun-2026 → resolve → re-route via Review & Approval with full stakeholder list.
- **Requirements** — see §8 below.
- **Executive view** — `LCDA_MVP1_ProjectPlan_Dbx_v5.xlsx`, "Executive View" tab. Reviewer-group columns split into Round 1 | Rework | Round 2. Source: "Val Activity" sheet of the project plan.
- **System Overview (SO)** — `System overview\LCDA_System_Overview.docx` generated 2026-06-08 from CSV TEMPLATE. Yellow highlights for dev-team items (OSS versions, architecture diagrams). Generator: `C:\Users\L132245\make_so.py`. Ready for TSME/BSME/SO/SC review routing once yellows resolved.
- **Playwright Test Automation Procedure (SOP)** — `LCDA_Playwright_Test_Automation_Procedure.docx` generated 2026-06-08. Adapted from LRL Product Delivery SOP. API mode only (no browser). Reviewers: TSME Liping/David, BSME Wendy, Val Engineer Aadesh. Approvers: TSO Carrie, BPO Sharon, CSQA Mansi. 15 yellow items for dev team. Generator: `C:\Users\L132245\make_playwright_sop.py`. New deliverable requested by Mansi (CSQA).
- **CR CHG2851220** — sent for re-route approval to Sharon (SO) + Poh (BQA); follow-up dispatched 5/21.

---

## 7. Codebase — `lly-lcda-dbx`

- **Repo:** `https://github.com/EliLillyCo/lly-lcda-dbx` (mirrored under `Deloitte-US-Consulting`)
- **Local clone:** `C:\Users\aamalviya\Downloads\LCDA Final\lly-lcda-dbx-dev`
- **Active branch:** `dev`

### Structure
```
projects/lcda/
├── databricks.yml                 # DAB bundle config (dev/qa/prod targets)
├── resources/jobs/data load/
│   └── LCDA_EXTRACTION_Job_workflow.yml   # Job: LCDA_EXTRACTION_JOB (tagged "TEST POC")
└── src/tasks/data load/
    ├── framework/
    │   ├── cdb_scehma_validation_with_audit.ipynb   # NOTE: typo "scehma"
    │   └── LCDA_STTM_TRANSFORMATION_FRAMEWORK.ipynb
    └── source/CDB/
        └── autoloader_with_logg.ipynb    # NOTE: typo "logg"
.github/workflows/dbx-deploy-lcda.yml     # CI/CD: dev/qa/main → dev/qa/prod targets
.pre-commit-config.yaml, .pylintrc, CODEOWNERS
```

### Job currently implemented
**`LCDA_EXTRACTION_JOB`** (Veeva CDB only):
1. `LCDA-CDB-SCHEMA-VALIDATION-TASK` → `cdb_scehma_validation_with_audit.ipynb` (params: catalog `cdb_source_catalog`, schema `cdb`)
2. `LCDA-CDB-AUTOLOADER-TASK` (depends on T1) → `autoloader_with_logg.ipynb`

### CI/CD trigger rules
- Push to `dev` or `feature/**` with `dev-deploy` in commit msg → deploy to **dev** target
- Push to `qa` → deploy to **qa** target
- Push to `main` → deploy to **prod** target
- Auth: OAuth M2M (`TF_DATABRICKS_CLIENT_ID` / `TF_DATABRICKS_CLIENT_SECRET`)

### Branching strategy (deck slide 21)
`feature/*` → `dev` (rebase + UT + PR) → `qa` → `main` (prod).
Approver ≠ contributor. PR requires 1 senior internal + 1 external reviewer.

### NOT YET in repo (gap to requirements)
- LabsConnect ingestion notebooks
- eCTS Oracle JDBC notebooks
- Raw → Refined → Conform transformation pipeline
- Health-check job
- SQL Warehouse API export layer
- Test folder (Playwright)
- Proper README (current README = "test branch")

### Open repo cleanups before SCR (LQP-302-26)
1. Fix `scehma` typo → `schema` (folder + file + workflow refs)
2. Remove "TEST POC" tag from job before prod
3. Delete stray `gg.sh` at root
4. Write proper README (purpose, build, deploy, env vars, contacts)
5. Add `tests/` folder for Playwright
6. Confirm secret rotation cadence with BISO
7. Confirm branch protection on `main` requires PR + CODEOWNERS approval

---

## 8. Requirements — current state

**Source file:** `LCDA_Phase1_Requirements_2026_05_14.xlsx` (Sheet1, 16 rows, 4 cols)
**Columns:** Acceptance Criteria / ALM upload | Topic | Status | Next step
**Classification decision:** **ALL Functional** (every row is "The system shall…") — confirmed with Prince. URS layer not needed because user/business need is captured in Project Charter / BRD.

### Row index (R# = sheet row #, header is R1)
| R# | Topic | Status | Issue summary |
|---|---|---|---|
| R2 | Veeva CDB ingestion | Soft Agreement - Complete | clean |
| R3 | LabsConnect ingestion | Soft Agreement - Complete | clean |
| R4 | eCTS incremental ingestion | Soft Agreement - Complete | **SCOPE-CONFIRM** (Jisi) |
| R5 | Data Integrity (5 statements) | Soft Agreement - Complete | clean (will split in ALM) |
| R6 | Audit Trail & Logging (4 statements) | Ready for Review | clean |
| R7 | Metadata Ingestion timestamps | (pending) | **NOT-SOURCEABLE** — drop "site local datetime", clarify "source system clock offset"; **GxP gap** — no NTP/time-sync AC (Sharon, Liping) |
| R8 | Lineage (4 statements) | Need review | line 2 "where applicable" HEDGE; line 4 "sufficient to explain" VAGUE + "e.g." OPEN-LIST |
| R9 | IAM (Platform + Data-Level + Audit) | Ready for Review | "Lilly-approved SSO" → name Entra ID; "Lilly-approved authentication" for SP → name mechanism; "per Lilly security standards" encryption x2 → cite LQP or TLS 1.2+/AES-256; "per the data-retention policy" → cite SOP. Lineage-access logging dropped — confirm with Mansi |
| R10 | Pipeline run logging + ingestion cycle | Ready for Review | "authorized users" minor; "configured retention policy" needs ref |
| R11 | Health Check | (pending) | **NOT-TESTABLE** — name critical components, alert channel/recipient/threshold/SLA, frequency, evidence/log clause (Liping, Carrie) |
| R12 | S3 Intelligent-Tiering | Ready for Review | SCOPE-CONFIRM (Sharon); cosmetic blank line |
| R13 | Security / vuln scanning | (pending) | **NOT-TESTABLE** — name Wiz, cite LQP numbers (Shubham), specify CIS profile/level (BISO), measurable AC (zero High/Critical at go-live) |
| R14 | Export / consumption API | (pending) | **NOT-TESTABLE** — specify HTTPS/TLS 1.2+, SSO/SP auth, list connectors (Databricks SQL Warehouse API, JDBC), add consumption logging AC |
| R15 | Orchestration schedule | (pending) | clean (refers to DS) |
| R16 | Backup (5 statements) | (pending) | line 1 "platform-native" → name Delta Time Travel + Deep Clone + S3 Versioning; line 2 retention window → cite DS/SOP; line 4 VCS not named → "Databricks Repos backed by Lilly GitHub Enterprise"; line 5 no RTO/RPO; **GxP gap** — annual restore-test cadence missing |

### Cross-cutting GxP gaps to ADD
| Gap | Suggested AC |
|---|---|
| Time sync | "All LCDA platform components shall synchronize system clocks to Lilly's enterprise NTP source." |
| Restore-test cadence | "The system shall execute a documented restore test of Delta Time Travel and S3 versioned objects at least annually, with evidence retained." |
| E-sig scope statement | "The system has no electronic-signature workflow in Phase 1; therefore 21 CFR Part 11 §11.50 / §11.70 controls are not applicable." (statement, not AC; goes in VTP) |
| Audit retention | "The audit trail shall be retained for a minimum of [X] years post record creation, per LCS retention policy [LQP-###]." |
| ALCOA+ statement | "All ingested GxP data shall preserve ALCOA+ attributes (Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available) through Landing → Raw → Conformed." |

### ALM wording rules to enforce
- ❌ Never use: `e.g.` / `such as` / `for example` / `including but not limited to` / `where applicable` / `where configured/available`
- ✅ Use: `the following:` + closed list, OR `as defined in DS §X.Y`
- Split bundled rows into atomic statements at ALM import time

### Open dependencies
| Owner | Input needed |
|---|---|
| Sharon Klein | Decide "site local datetime" deferral |
| Shubham | LQP numbers for InfoSec policies |
| BISO (Shawn/Tim) | CIS benchmark profile/level |
| Liping / David | Critical-component list for health checks |
| Carrie | Alert channel + retention policy references |

---

## 9. SOPs available (locally)

`C:\Users\aamalviya\Downloads\LCDA Final\Lilly_SOPs\`

### 9.1 LCS-106 — IT Asset and Configuration Management
**Purpose:** Maintain an accurate inventory of IT assets in compliance with LQS-302; maximize business value, optimize cost, mitigate risk, enable informed decisions.
**Scope:** All IT assets and corresponding Configuration Items (CIs) maintained in the enterprise ServiceNow CMDB.
**Key content:** IT Asset lifecycle (Propose → Build/Acquire → Deploy → Manage & Support → Retire); Configuration Model; CI naming & sourcing; CI relationships; CMDB security; processes to create/maintain/verify/retire CIs.
**LCDA relevance:** Defines how the LCDA Business Application CI is registered, classified (RC#4, GMP), and linked to Application Service / platform CIs in ServiceNow — drives change approval routing.

### 9.2 LCS-501 — Lilly IT Change Management using ServiceNow
**Purpose:** Provide an accurate, consistent, verifiable procedure for executing Lilly IT Change Management in ServiceNow.
**Scope:** Lifecycle of changes to IT assets in controlled environments (production + any environment designated as controlled). Covers hardware, network, storage, databases, applications, data center facilities, and externally managed SaaS/PaaS.
**Change types:** Pre-Approved, Normal, Expedited, Emergency.
**Approval routing:** Driven by whether component is an **Application** (Business Application CI with Quality Workflow = "Validation" — LCDA's case) or **Platform** (Quality Workflow = "Qualification") — Appendix A vs Appendix B.

**LCS-501 — Emergency Change (key facts)**
- **Definition (CMP-09):** Change needed quickly to (a) keep a critical business process running (failure impacts product/data quality), (b) restore compromised integrity of system or data, or (c) minimize security/safety/environmental risk.
- **Procedure:** §7.8 Plan/Schedule/Approve (incident record MUST be attached at E-1.1) → §7.9 Coordinate & Deploy → §7.10 Review & Close
- **Approvals (Appendix A, validated systems, LCDA):**
  - Dev + Deploy: **No ServiceNow approvals required** — verbal/email per LQP-302-25; must be documented inside the SN record
  - Closure for Emergency Deploy/System/Release (GMP): **Technical Approver Group + System Quality Group**
- **SLA (CMP-16):** Document, approve, and close within **20 working days** post-implementation for applications (5 days for infrastructure). Exceeding requires documented justification accepted by all closure approvers.

### 9.3 LQP-302-25 — Risk Evaluation and Responsibilities for Computer Systems
**Purpose:** Classify computer systems into risk categories and define QA oversight + approval requirements.
**Risk Categories:**
- **RC#5** — GMP High and Medium Criticality Data
- **RC#4** — GMP Low Criticality Data, GCP/GVP High Impact, systems requiring independent QA oversight ← **LCDA**
- **RC#3** — High Regulatory Impact
- **RC#2** — Other Regulatory Impact
- **RC#1** — Low Risk Computer Systems
**Key content:** QA approval requirements per risk category; validation strategy + artifacts; ongoing risk evaluation; approvals & agreements; lists of typical validation artifacts/deliverables; change control approval/agreement matrix.
**LCDA relevance:** Source of truth for what artifacts and approvals are required for LCDA Phase 1 (the section "Typical Validation Process Artifacts/Deliverables" lists VTP, Requirements, DS, System Overview, Coding Standards, Security Plan, Admin SOP, Audit Trail Assessment, Test cases — i.e., LCDA's deliverable list).

### 9.4 LQP-302-26 — Computer Systems Delivery
**Purpose:** Define the delivery (build/validate) lifecycle for new computer systems and major releases.
**Key sections:**
- §1 Validation Overview & Process
- §2 Delivery Artifacts + Computer System Inventory
- §3 Planning Activities
- §4 Third Party Management (CDA/NDA, assessments, agreements)
- §5 Requirements: documentation, **User / Functional Requirements (§5.2)**, Electronic Records/Signatures Part 11 (§5.3), Security (§5.4), Data (§5.5), Other (§5.6), Approval & Traceability (§5.7)
- §6 Design: System Overview, Config Spec, Design Spec
- §7 Development: Coding/Programming Standards (§7.2), **Source Code Review (§7.3)**, Open Source (§7.4), Installation Qualification (§7.5)
- §8 Testing: Unit/Integration (§8.1), System (§8.2), Acceptance (§8.3), Other types (§8.4), Test Planning (§8.6), Test Scripts/Cases/Execution (§8.7), Test Reporting (§8.8)
- §9 Deployment: System Acceptance, Deployment
**LCDA relevance:** Governs everything from requirements wording (URS vs FR), through DS, through coding standards, through SCR (§7.3 cited in LCS-501 E-1.2 for Emergency Changes), through formal testing. This is the SOP the VTP is built against.

### 9.5 LQP-302-27 — Computer System Support and Maintenance
**Purpose:** Define support, maintenance, change control, and retirement for production computer systems.
**Key sections:**
- §2 Support and Maintenance Validation Artifacts (incl. Security)
- §3 Third Party Management
- §4 **Computer System Change Control**: System Changes (§4.3), Data Changes / Data Loads (§4.4), Abandoned Changes (§4.5), **Emergency Changes (§4.6)**, Documentation-Only Changes (§4.7)
- §5 Supporting Processes: Incident & Problem Mgmt, System Audit Trail Review Expectations (§5.2), **Back-up & Restoration (§5.3)**, **Disaster Recovery (§5.4)**, **BCP (§5.5)**, Temp Electronic Media, User Training, System Admin & Support, Quality Agreements
- §6 Periodic Review
- §7 Computer System Retirement
**LCDA relevance:** Governs the **System Admin & Support SOP**, **BCPDRP**, **System Audit Trail Assessment**, periodic review plan, and the change-control runbook for production LCDA.

### 9.6 LQP-302-29 — Computer System and Platform Security
**Purpose:** Define security planning and ongoing security maintenance for computer systems and platforms.
**Key sections:**
- §1 Security Overview, Unmet Security Requirements, Physical & Logical Security
- §2 Security Planning:
  - §2.1 Identity, Authentication, Access Management (SSO, MFA, RBAC, provisioning)
  - §2.2 Application and Software Security (SAST/DAST, vuln scanning, secure SDLC)
  - §2.3 Data Security (encryption in transit/at rest, classification, masking)
  - §2.4 Endpoint Security
  - §2.5 Network Security
  - §2.6 Third Party Management
- §3 Maintenance of Security: Security Admin, Logical Security, Physical Security
**LCDA relevance:** Governs the **Security Plan & Security Admin SOP**, the IAM requirements (R9), the vuln-scanning requirement (R13 — Wiz/Checkmarx), encryption ACs, BISO sign-off, and Entra ID/MyAccess provisioning model.

### 9.7 LQP-302-30 — Artificial Intelligence and Machine Learning Computer System Validation
**Purpose:** Validation expectations for AI/ML-based computer systems (custom ML models or fine-tuning of pre-trained models).
**Key sections:** AI/ML acronyms; validation overview; development expectations; AI/ML-specific evaluation metrics; design considerations for ML; training/testing of custom or fine-tuned models; production deployment; change control specific to ML drift; ongoing monitoring (concept drift, data drift).
**LCDA relevance:** **NOT in Phase 1 scope** (no agentic/ML features — deck slide 4 explicitly excludes "Agentic processes"). Kept for reference if AI is added in a later release.

---

## 10. Working environment & gotchas

### Shell — Windows PowerShell 5.1
- ❌ NO heredocs in PowerShell — write a `.py` file and execute it
- ✅ Use `$env:PYTHONIOENCODING="utf-8"` BEFORE any `python -c` that prints unicode (→ — etc.)
- ❌ Don't use `&&` — chain with `;`
- ✅ When file writes need UTF-8, write inside Python with `open(...,encoding='utf-8')`, NOT via `Out-File` (which defaults to UTF-16 BOM)

### Python deps installed (3.13)
`openpyxl`, `python-docx`, `python-pptx`, `pypdf`, `pymupdf 1.27.2.3`

### Common errors I've hit
- `PermissionError [Errno 13]` on Excel save → file is open in Excel → save to incremented filename (v4 → v5)
- `'charmap' codec can't encode` → set `PYTHONIOENCODING=utf-8` and write to file with explicit encoding
- PDF annotation reads returning 0 → comments are baked into page text, extract via `page.get_text()` not annotations

---

## 11. Key files in workspace

`C:\Users\aamalviya\Downloads\LCDA Final\`

| File | What it is |
|---|---|
| `LCDA Validation and Test Plan_1.1.docx` | Latest VTP (Word — open and Update TOC) |
| `LCDA_Phase1_Requirements_2026_05_14.xlsx` | Current requirements (16 rows) — see §8 |
| `LCDA_MVP1_ProjectPlan_Dbx.xlsx` | Source project plan (sheets: Project Plan_latest, Project Plan, Deliverables Tracker, **Val Activity**, Sheet1) |
| `LCDA_MVP1_ProjectPlan_Dbx_v5.xlsx` | Executive View v5 (reviewer-group columns, R1/Rework/R2 split) |
| `LCDA Validation and Test Plan_1.0 (3).pdf` | Original PDF with 50 reviewer comments |
| `Data Agg - Databricks Options 1.pptx` | 80-slide architecture deck — confirmed catalog names, schema names, ETL pipeline steps per source, job schedules, open dev items, sprint timeline, Path A/B decision. Extracted 2026-06-09. |
| `Lilly_SOPs/` | All 7 SOPs (see §9) |
| `lly-lcda-dbx-dev/` | Cloned code repo (see §7) |
| `build_exec_view.py` | Script that builds the exec-view sheet |
| `update_vtp.py` | Script that applied the 50 PDF comment fixes |
| `patch_regression.py` | Script that added §2.6 Regression to VTP |
| `deck_content.txt` | Plain-text dump of the deck |
| `lcs501_full.txt` | Plain-text dump of LCS-501 with tables |

---

## 12. Architectural diagrams (slide pointers)

| Slide | Topic |
|---|---|
| 4 | Path A vs Path B (Start on EDB Dev → choose) |
| 5–6 | Phase 1 timeline (5/18 → 7/31) |
| 7 | Physical architecture |
| 8–9 | Logical architecture (D0/D1/D2 layers) |
| 10 | Framework design (Landing → Raw → Refined) |
| 11–12 | CDB Raw + Refined load strategy (~7,000 raw → ~80 refined master tables) |
| 13, 17 | Pipeline orchestration (job-per-source, parallel/sequential tasks) |
| 14–16 | Monitoring & alerting (audit + log table schemas) |
| 18–19 | Failure recovery / repair-run scenarios |
| 20–24 | Config / STTM / GitHub branching / DAB deployment |
| 25 | Data masking (UC UDF, RBAC) |
| 26–31 | Source ingestion details (CDB ZIPs, LabsConnect, eCTS RTSM tables) |
| 32 | Delta lake catalog naming (`lly_lcda_raw_dev` etc.) |
| 33 | Solution Architecture MVP1 walkthrough (steps ①–⑮) |

---

## 13a. Sprint timeline (from deck slide 7 — MVP1 confirmed schedule)

| Date | Milestone |
|---|---|
| 2026-05-18 | Databricks EDB Dev access provisioned (DBX Access) |
| 2026-05-18 to 05-29 | Dev platform setup completion (cluster, VPC, services) |
| 2026-05-25 | SDLC Documentation start; ETL Framework design start |
| 2026-06-01 | Informal Testing start (test scripts designed per sprint) |
| 2026-07-17 | ETL Complete (Dev complete milestone) |
| 2026-07-31 | Phase 1 MVP — full scope in EDB Dev |

**Sprint breakdown:**
- **S0:** Architecture review; User roles; SP identity setup; UC schema grants; Platform setup; DEV Platform Build + Cluster setup + VPC
- **S1:** ETL Framework design; Audit Tools + Lineage + Load Tools (Raw → Refined)
- **S2:** Extraction Tools + Schema Validation → Raw layer; Raw layer live
- **S3:** Refined Layer ready; Workflows Orchestration + Refined data access through API
- **S4:** Integration Testing (3 sources); Schema validation E2E; SP identity verify; RBAC boundary (conform only); Test scripts ready
- **S5:** SAE Review; Validation & Test Plan Draft; Design Specification; Coding Standards; Requirements approval in ALM; System Overview & Configuration Specification (draft); Test Automation Framework setup & build; System admin SOP (draft); Security plan & Security admin SOP (draft); System Audit trail review assessment (draft); CR Dev approved; Data Quality Tool; Bug fixes; E2E data loads; Access/API ready

**Path A vs Path B (QA/Prod decision pending — re-evaluate by 2026-06-26):**
- **Path A (current Phase 1):** EDB Dev (non-HIPAA) → EDB QA (HIPAA) → EDB Prod (HIPAA); requires HIPAA BAA with Databricks + SLA with EDB team
- **Path B (deferred):** EDB Dev → LCDA Dev → LCDA QA → LCDA Prod (HIPAA); requires independent Databricks account + 4 weeks additional migration effort

**Architecture decision rationale (weighted matrix from deck):**
- Databricks on AWS: 8.25 — primary platform selected
- AWS Native: 7.15
- Key drivers: Delta Lake ACID + Time Travel satisfies 21 CFR Part 11 natively; Unity Catalog auto-lineage; Auto Loader 10× throughput vs Glue for file-heavy ingestion (150–500 files/day)

### Future / Phase 2 — Agentic architecture (out of Phase 1 scope)
7 specialized agents planned for future phases:
1. Schema Validation Agent
2. STTM (Source-to-Target Mapping) Agent
3. Pipeline Auditing & History Agent
4. Clinical Data Review (DQ) Agent
5. Medical Monitoring Agent
6. Query Manager Agent
7. Third-party Data Upload Agent

MCP Server API consuming Delta Lake + Unity Catalog; Genie NL-to-SQL; Vector Search RAG; Mosaic AI.

---

## 13. Pending work

> **Session update 2026-06-19:**
> - eCTS confirmed out of scope for Phase 1 — remove from all documents
> - VTP has 60+ reviewer comments — significant rework required before re-routing (see §16 for reviewer profiles)
> - Study Onboarding requirement added: REQ-ONBOARD-01 and REQ-ONBOARD-02 — needs to be added to ALM and VTP (via CR after current review closes)
> - API and ETL testing to be called separately (not "API/ETL") per test lead direction
> - Playwright SOP (CT Space generic) routed in QDocs — review deadline 2026-06-26

1. Get Sharon + Poh approval on CR CHG2851220 (follow-up sent 5/21 — still pending as of 5/26)
2. After requirements finalized → route to Mansi for CSQA review
3. Once VTP v1.1 reviewed → Word "Update Table" to refresh TOC
4. Code repo: add LabsConnect + eCTS notebooks; fix `scehma` typo; remove "TEST POC" tag; write proper README
5. **[DONE]** System Overview — `System overview\LCDA_System_Overview.docx` generated; 26 yellow items pending dev input. Next: route for review once yellows resolved.
6. **[DONE]** Playwright Test Automation Procedure — `LCDA_Playwright_Test_Automation_Procedure.docx` generated; 15 yellow items pending dev input. Next: route to Mansi/team once yellows resolved.
7. **[DONE]** AI-in-validation walkthrough email drafted for scheduling call with senior teams.
8. Apply R10/R12/R13 testability fixes to requirements xlsx
9. Clone LCDA testing repo (`lly-lcda-testing-framework`) from GitHub Enterprise — need Contributor access from Karthiga
10. **[IN PROGRESS]** Playwright framework adaptation — `playwright-base-framework` npm installed; next: add `helpers/databricks-client.ts`, adapt `playwright.config.ts`, add test files (pipeline-audit, rbac, schema, data-integrity)

---

## 14. Dev environment — current state (as of 2026-05-26)

### Node.js / npm
- **Portable Node.js** v22.15.0 installed at `C:\Users\L132245\nodejs\`
- npm v10.9.2
- **Global npm registry:** `https://elilillyco.jfrog.io/artifactory/api/npm/npm/`
- **Auth token:** configured permanently in `C:\Users\L132245\.npmrc` (identity token, `_authToken` format)
- **Artifactory access:** granted — identity token generated from `elilillyco.jfrog.io`
- Install command for any project: `& "$env:USERPROFILE\nodejs\npm.cmd" install --ignore-scripts`

### Playwright framework (confirmed from codebase 2026-06-08)
- **Location:** `C:\Users\L132245\OneDrive - Eli Lilly and Company\Desktop\LCDA Phase1\Automation Testing\lly-lcda-testing-framework\`
- **Repo:** `lly-lcda-testing-framework` (Deloitte-US-Consulting GitHub Enterprise)
- **Status:** Framework fully set up. One smoke test exists (`tests/smoke/check-dbx-query.spec.ts`). LCDA-specific tests not yet written.
- **Authentication:** OAuth M2M (service principal) via AWS Secrets Manager — NOT personal access token. Flow: `.env.dev` AWS IAM keys → Secrets Manager secret `lcda/dev/databricks` → `{ host, httpPath, clientId, clientSecret, catalog, schema }`
- **Key files:**
  - `utils/dbx-helper.ts` — DBSQLClient openSession / queryDbx / closeDbx
  - `utils/secrets-helper.ts` — AWS SM fetch, cached in-memory
  - `utils/logger-helper.ts` — colored logger, LOG_LEVEL-gated
  - `utils/constants.ts` — empty placeholder
  - `core/fixture.ts` — custom test fixture with env annotations
  - `core/global-setup.ts` — warms up DBX connection if `CONNECT_TO_DBX=TRUE`
  - `core/global-teardown.ts` — closes DBX session
  - `core/generate-single-file-report.js` — creates standalone HTML in `test-reports/`
  - `config/dev.json` — `{ aws-region, secret-name }`
- **Env var structure (3 sources):**
  - `.env` (common): `LOG_LEVEL`, `PARALLEL_EXECUTION`, `TEST_ENV`
  - `.env.dev`: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION`, `DBX_SECRET_NAME=lcda/dev/databricks`
  - Shell (runtime): `CONNECT_TO_DBX=TRUE`
- **npm registry:** `https://elilillyco.jfrog.io/artifactory/api/npm/Lilly-NPM/` (token: `JF_ARTIFACTORY_TOKEN`)
- **Execution (PowerShell):** `$env:TEST_ENV="dev"; $env:CONNECT_TO_DBX="TRUE"; npx playwright test --grep "@smoke"`
- **Test tags:** `@smoke` (basic connectivity), `@dbx` (Databricks queries)
- **CI/CD:** GitHub Actions `run-playwright-tests.yml` — workflow_dispatch, runs on ubuntu-latest, uses GitHub environment secrets for AWS creds
- **LCDA tests to write:** pipeline-audit.spec.ts, rbac.spec.ts, schema.spec.ts, data-integrity.spec.ts

---

## 15. GRRS Revision 22 — Retention findings (as of 2026-05-26)

**Source:** `GRRS_Revision_22-EN.pdf` (152 pages, effective 2025-09-05)

### Key record classes for LCDA

| Record Class | Covers | Retention (Global) | Trigger |
|---|---|---|---|
| **NOTE-A** | ALL CSV docs: IQ/OQ/PQ, audit trails, app logs, RBAC, change control, code, test evidence | Inherits PDMS-006 = **30–31 years** | — |
| **PDMS-006** Clinical Development | Raw EDC data (clinical study databases) — **controls NOTE-A** | Max **31 years** | Life of Compound/Product |
| **INSY-002** Platform Logs | Firewall, infrastructure access, network, platform activity logs | Max **2 years** | Creation |
| **INSY-001** IT Qualification Artifacts | Platform qualification docs (overridden to 31 yrs by NOTE-A) | Max **16 years** base | Platform Inactive |
| **QLAS-001** Quality Systems | GxP SOPs, change control, CAPAs, deviations, audit reports | Max **26 years** | No Longer Active |
| **TNDV-001/002** Training | Course materials + individual completion records | Max **31 years** | Superseded / Employee Exit |
| **ADMN-001** Temporary Records | Data backups (working copies), drafts | Max **2 years** | Creation |

### Confirmed requirement (X = 2)
> "The system shall retain logs such as Firewall logs, Infrastructure Access Logs, Infrastructure Security Logs, Network System Logs, Platform Activity Logs for a period of maximum **2** years as per Revision 22 of the Global Records Retention Schedule (INSY-002)."

### Key distinctions
- Application audit trail (ALCOA+ records in Databricks) → NOTE-A → PDMS-006 → **31 years** (NOT 2 years)
- LCDA as secondary analytics layer: manager's view is INSY-001 (16 yrs) for platform docs; NOTE-A strict reading gives 31 yrs — **needs QA decision documented in VMP**
- Data backups that are only working copies → ADMN-001 (2 yrs); if system of record → PDMS-006 (31 yrs)

---

## 16. Reviewer profiles & pre-routing checklist

> Run this section before routing ANY document. Failure to do so results in 50+ comments, rejects, and re-routing cycles.

### 16.1 Reviewer profiles

**Mansi Agarwal — CSQA** *(most thorough, most comments, hardest to satisfy)*
- Always checks: correct GSOP/CSA Launchpad template version, all required validation artifacts present or justified, risk evaluation completeness (resources + data integrity + audit trail + deployment risks), UAT must be formal with documented evidence for GCP systems, Requirements Management section present, security testing described against security requirements (not as Cyber/SAST process), font/formatting/blank pages/table numbers, defects in ALM only
- Will flag: AI/ML paragraph if not applicable, "platform" language, informal UAT, missing BCPDRP/Audit Trail/Source Code Review artifacts, Jira referenced for GxP defects

**Poh Chiam Sim — BQA**
- Always checks: every undefined term or jargon, testing prerequisites (testers qualified, trained, requirements approved in ALM), formal UAT requirement, defect pass/fail criteria clarity, all source system test environments named, document management system named explicitly
- Will flag: "secondary repository", "business-ready", "overall effectiveness", vague phrases, UAT called informal

**Wendy Huber — BSME**
- Always checks: Phase 1 scope accuracy vs business agreement, "later phases" not "Phase 2 and/or Phase 3", data migration bullet (premature), outbound interface as enablement only, table numbering consistency, table caption style consistency, BSME vs BPO role title, test data language (collaboration with business team)
- Will flag: specific phase numbers, premature scope items, wrong role titles, Terms & Definitions placement

**David Cantrell — TSME**
- Always checks: source system environment specifics, correct product/tool names, accurate description of what system does vs enables, scope boundary per interface, "platform" language
- Will flag: wrong environment names, factual errors in technical descriptions, "platform"

**Liping Cai — TSME**
- Always checks: product name spelling (LabsConnect one word, Veeva Vault CDB), tool list completeness (WIZ present), correct acronym expansions (EDB = Enterprise Data Backbone), PySpark / Databricks separated
- Will flag: "Labs Connect" (two words), missing tools, wrong EDB expansion, "platform"

**Carrie Wertz — TSO**
- Always checks: testing environment decisions, stakeholder responsibilities, process alignment with Lilly standards
- Minimal comments but focused on process correctness

---

### 16.2 Master pre-routing checklist

Run before sending ANY document for review. Check every item. Zero exceptions.

**Formatting & structure**
- [ ] No blank pages anywhere in the document
- [ ] Consistent fonts throughout — Calibri 11pt body
- [ ] All table numbers sequential and correct (Table 1, 2, 3... not Table 21, Table 32)
- [ ] Table caption style consistent — either all headers or all footers, not mixed
- [ ] No extra blank rows or spaces inside tables
- [ ] No blue backgrounds on tables unless template-required
- [ ] TOC updated and accurate

**Terminology — global find and replace before routing**
- [ ] "platform" → "system" (everywhere except Databricks platform qualification reference)
- [ ] "Labs Connect" → "LabsConnect" (one word, always)
- [ ] "Phase 2 and/or Phase 3" → "later phases"
- [ ] "documented requirements" → "approved requirements"
- [ ] "system testing" → "system integration testing" (consistently)
- [ ] EDB expanded as "Enterprise Data Backbone" not "Enterprise Databricks"
- [ ] "PySpark (Databricks)" → "PySpark / Databricks"
- [ ] Veeva CDB or Vault CDB — confirm correct full name with dev team and use consistently
- [ ] "secondary repository" → remove "secondary"

**Content — CSQA/BQA will always check these**
- [ ] Correct GSOP/CSA Launchpad template version — confirm with Mansi before starting
- [ ] All validation artifacts in deliverables table OR written justification for each excluded one
- [ ] Risk evaluation includes: resources, data integrity risks, audit trail risks, release/deployment risks
- [ ] Acceptance Testing (UAT) written as FORMAL with documented evidence — never "informal"
- [ ] Requirements Management section present
- [ ] Security testing described against actual security requirements — not as SAST/Cyber process
- [ ] Defects tracked in ALM — no Jira reference in any formal testing section
- [ ] All undefined terms in Terms and Definitions section
- [ ] Testing prerequisites include: testers qualified and trained, requirements approved in ALM
- [ ] All source system test environments named explicitly
- [ ] Document management system named (QualityDocs)
- [ ] AI/ML section removed if not applicable
- [ ] "e.g.", "such as", "where applicable", "including but not limited to" — removed from all ACs

**Scope & technical accuracy — TSME/BSME will check these**
- [ ] Scope matches what business agreed — reviewed with Wendy before routing
- [ ] Technical content reviewed with dev team (David/Liping/Govind) before routing
- [ ] eCTS removed from all Phase 1 scope statements (confirmed out of scope 2026-06-19)
- [ ] Outbound SQL Warehouse described as interface enablement only — not active data sharing
- [ ] Source system environments named correctly
- [ ] Tool list complete: WIZ, Checkmarx (SAST + SCA), GitHub, Databricks Jobs, ALM (testing tool — not dev tool)

**Role titles — use exactly these**
- [ ] Sharon Klein = System Owner (SO) or Business Process Owner (BPO) — consistent throughout
- [ ] Carrie Wertz = Technical System Owner (TSO) — consistent throughout
- [ ] Wendy Huber = BSME (not BPO)
- [ ] Mansi Agarwal = CSQA
- [ ] Poh Chiam Sim = BQA

---

## 17. Email templates / phrasing reuse

### Subject lines used
- `CR CHG2851220 — LCDA Architecture Update | Routed for your approval`
- `Follow-up: CR CHG2851220 — Pending your approval`
- `LCDA Phase 1 Requirements — Going to ALM as Functional`

### Aadesh sign-off
```
Thanks,
Aadesh
```

---

## 18. Quick boot prompt for a new chat

If starting fresh elsewhere, paste this into the new chat first:

> "I'm Aadesh, validation engineer on Lilly LCDA Phase 1 (RC#4 GxP). Architecture is Databricks-centric (EDB workspace) on AWS S3 — CR CHG2851220 approved. Validation deliverables (VTP, Requirements, DS, Coding Standards, System Overview, Security Plan + Admin SOP, System Admin & Support SOP, System Audit Trail Assessment) are in review with reviewer groups (VAL+BSME / TSME,BSME,SO,SC / TSME / CSQA / BISO / BQA & CSQA). Read `LCDA_MASTER_CONTEXT.md` for the full state."
