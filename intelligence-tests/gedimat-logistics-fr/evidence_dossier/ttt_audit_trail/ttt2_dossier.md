# IF.TTT DOSSIER 02
Source: `ttt2.txt`
Purpose: Reconstructed audit trail of the captured Claude UI session log
Scope: All meaningful structured data extracted from the JSON-like diff in the file

## 1. Session Metadata
- cloud_repl_id: d18a1db7-0275-805f-beaa-db08772eb5cd
- cloud_ui_host_id: 7d206b09-393d-48c5-814f-36b526479e87
- cloud_ui_session_id: ed9d1ae7-8f55-4a6d-a4f8-686dd07ace45
- created_at_iso: 2025-02-08T13:56:24.593Z
- cwd: /home/llm
- pid: 20140
- port: 46679
- state: active

## 2. Billing & Runtime Configuration
- billing.enabled: false
- billing.account_balance: 0.0
- api_file_upload_mebibyte_limit: 99
- max_containers: 10000

## 3. Enabled Features / Flags
- analytics.enabled: false
- prompts.enabled: true
- sql.enabled: true
- ui_editor.enabled: true
- ssh.enabled: true
- connected_apps.enabled: true
- local_files: path=/mnt/data, readwrite=true

## 4. LLM Config
- default_api_key: (empty)
- codemodel: false

## 5. Raw Extract (abbreviated)
See `ttt2_raw.json` for full machine-readable extraction.

## 6. Integrity Notes
- No diff collisions detected.
- All parsed fields preserved verbatim where present.

## 7. Provenance
- Extracted from uploaded file `ttt2.txt` on 2025-11-17T02:42:26.245972Z by assistant.
