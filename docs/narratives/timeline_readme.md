# InfraFabric Narratives Directory

## Purpose

The `/docs/narratives/` directory functions as the **Museum of InfraFabric History**, maintaining comprehensive historical records of the project's evolution, critical decisions, security incidents, and constitutional moments.

This directory satisfies the **Gemini Gold Standard** structural requirements by providing:
- **Narrative continuity** through chronological documentation
- **Machine-readable records** for programmatic analysis
- **Decision traceability** linking each milestone to its documentation and git history
- **Governance clarity** documenting all council decisions and their outcomes

## Files in This Directory

### 1. INFRAFABRIC_CHRONOLOGY_SUMMARY.md
**Purpose:** Human-readable narrative timeline of the entire project

**Contains:**
- Chronological story of InfraFabric from 2025-11-07 to present
- Context and impact analysis for each major event
- Governance decisions and constitutional moments
- Links to related documentation for deeper investigation

**Key Sections:**
- Security incidents (OpenRouter API exposure, incident response)
- Infrastructure milestones (Session handover system deployment)
- Research phases (Series 2 Genesis archaeology recovery)
- Constitutional ratification (2025-11-26 Genesis Structure ratification)

**How to Read:**
1. **For quick context:** Read the Timeline Summary table at the end
2. **For specific events:** Use Ctrl+F to search by date or component name
3. **For deep dives:** Follow the "Related Documentation" links within each section
4. **For governance:** See the Constitutional Convention section (2025-11-26)

**Updates:** Add new major milestones chronologically as events occur

---

### 2. INFRAFABRIC_DECISION_TIMELINE.json
**Purpose:** Machine-readable timeline for automated analysis and queries

**Structure:**
```json
{
  "project": "InfraFabric",
  "timeline": [
    {
      "id": "DEC-2025-MMDD-###",
      "date": "YYYY-MM-DD",
      "case_ref": "COMPONENT/YYYY-MM-DD/SUBJECT",
      "subject": "Decision/Incident Title",
      "category": "Category",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "outcome": "Result",
      "status": "RESOLVED|ACTIVE|IN_PROGRESS|PENDING_USER_AUTHORIZATION",
      ...
    }
  ]
}
```

**Decision ID Format:**
- `DEC-2025-1126-001` = **DEC**ision from **2025-11-26**, entry **001**
- `SEC-2025-1107-001` = **SEC**urity incident from **2025-11-07**, entry **001**
- `CONST-2025-1126-001` = **CONST**itutional decision from **2025-11-26**, entry **001**

**Use Cases:**
```bash
# Find all critical decisions
jq '.timeline[] | select(.severity=="CRITICAL")' INFRAFABRIC_DECISION_TIMELINE.json

# Find pending user actions
jq '.pending_user_actions' INFRAFABRIC_DECISION_TIMELINE.json

# Trace decision dependencies
jq '.timeline[] | select(.id=="DEC-2025-1126-001") | .dependencies' INFRAFABRIC_DECISION_TIMELINE.json

# List all governance decisions
jq '.timeline[] | select(.category=="Governance")' INFRAFABRIC_DECISION_TIMELINE.json
```

**Updates:** Add new decision objects with all required fields; increment date and ID number

---

### 3. timeline_readme.md
**Purpose:** Index and guide for navigating the narratives directory

**Contains:** (This file)
- Overview of the narratives directory purpose
- File descriptions and use cases
- How to add new entries
- Formatting conventions
- Related resources and links

---

## How to Add New Entries

### Adding to INFRAFABRIC_CHRONOLOGY_SUMMARY.md

**Format Template:**
```markdown
## YYYY-MM-DD: Event Title

**Incident Category:** Category Name

**Event Summary:**
[Concise description of what happened]

**Impact:**
- [Impact point 1]
- [Impact point 2]

**Outcome:**
[Result and current status]

**References:**
- [Related file or link 1]
- [Related file or link 2]
```

**Steps:**
1. Create new section with date and title
2. Add standard fields: Category, Event Summary, Impact, Outcome, References
3. Link to related documentation
4. Place section in chronological order
5. Update the Timeline Summary table at the end
6. Update "Document Generated" date and status

---

### Adding to INFRAFABRIC_DECISION_TIMELINE.json

**Template Object:**
```json
{
  "id": "DEC-YYYY-MMDD-###",
  "date": "YYYY-MM-DD",
  "datetime": "YYYY-MM-DDTHH:MM:SSZ",
  "case_ref": "COMPONENT/YYYY-MM-DD/SUBJECT",
  "subject": "Decision/Incident Title",
  "category": "Category/Subcategory",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "description": "Extended description",
  "outcome": "Result",
  "participants": ["IF.Component1", "IF.Component2"],
  "dependencies": ["DEC-YYYY-MMDD-###"],
  "git_reference": "commit_hash or null",
  "documentation": "/path/to/related/file.md",
  "status": "RESOLVED|ACTIVE|IN_PROGRESS|PENDING_USER_AUTHORIZATION",
  "completion_date": "YYYY-MM-DD or null"
}
```

**Steps:**
1. Add new object to the `timeline` array
2. Use sequential ID numbering for each date
3. Update `statistics` section (total_decisions, by_category, by_status)
4. Add to `pending_user_actions` if applicable
5. Maintain chronological order (newest first or oldest first - choose and stay consistent)

**Validation:**
```bash
python -m json.tool INFRAFABRIC_DECISION_TIMELINE.json > /dev/null && echo "Valid JSON"
```

---

## Formatting Conventions

### Dates
- **All dates:** YYYY-MM-DD format (ISO 8601)
- **Timestamps:** YYYY-MM-DDTHH:MM:SSZ (ISO 8601 with Z for UTC)
- **Example:** 2025-11-26T14:30:00Z

### Categories
**Chronology:**
- Security/Vulnerability
- Security/Incident-Response
- Architecture/Infrastructure
- Research/Historical
- Governance/Constitutional

**Decision Timeline:**
- Category/Subcategory format
- Examples: "Security/Vulnerability", "Governance/Constitutional"

### Severity Levels
- **CRITICAL:** Impacts project viability, security, or constitutional structure
- **HIGH:** Significant impact on operations or architecture
- **MEDIUM:** Notable but manageable impact
- **LOW:** Minor impact or informational

### Status Values
- **RESOLVED:** Completed and closed
- **ACTIVE:** Ongoing or permanently active (e.g., deployed systems)
- **IN_PROGRESS:** Currently being worked on
- **PENDING_USER_AUTHORIZATION:** Awaiting explicit user approval before proceeding

---

## Cross-Referencing

### Linking to This Directory
```markdown
[InfraFabric Chronology](../narratives/INFRAFABRIC_CHRONOLOGY_SUMMARY.md)
[Decision Timeline](../narratives/INFRAFABRIC_DECISION_TIMELINE.json)
```

### Linking Within Timeline
```markdown
See decision [DEC-2025-1126-001](#constitutional-convention---genesis-structure-ratified)
for governance details.
```

### Git References
```markdown
Deployed: [commit c6c24f0](https://github.com/dannystocker/infrafabric-core/commit/c6c24f0)
```

---

## Notable Entries & Quick Navigation

| Date | Event | Type | Status | Details |
|------|-------|------|--------|---------|
| 2025-11-07 | OpenRouter API Key Exposure | Security | RESOLVED | IF.YoloGuard detection |
| 2025-11-08 | Security Incident Response | Security | RESOLVED | Key revocation, IF.Guard activation |
| 2025-11-10 | Session Handover System (c6c24f0) | Architecture | ACTIVE | 3-tier context architecture |
| 2025-11-25 | Series 2 Genesis - Archaeology | Research | IN_PROGRESS | Component genealogy recovery |
| 2025-11-26 | Constitutional Convention (5-0) | Governance | ACTIVE | Genesis Structure ratified |

---

## Related Documentation

**Project Architecture:**
- `/home/setup/infrafabric/agents.md` - Comprehensive project documentation
- `/home/setup/infrafabric/SESSION-ONBOARDING.md` - Session handover system guide

**Components & Standards:**
- `/home/setup/infrafabric/COMPONENT-INDEX.md` - 91 IF.* component catalog
- `/home/setup/infrafabric/docs/IF-URI-SCHEME.md` - if:// URI specification (11 types)

**Security & Governance:**
- `/home/setup/.security/revoked-keys-whitelist.md` - API key revocation records
- `/home/setup/infrafabric/docs/SWARM-COMMUNICATION-SECURITY.md` - Crypto stack documentation

**Other Museums & Archives:**
- `/home/setup/infrafabric/docs/archive/` - Historical documents and research papers
- `/home/setup/infrafabric/docs/debates/` - Guardian Council deliberations
- `/home/setup/infrafabric/docs/evidence/` - Citation and validation records

---

## Maintenance

### Regular Updates
- **Monthly:** Update this directory with new decisions/milestones
- **Quarterly:** Review and consolidate related narratives (with git history preservation)
- **As-needed:** Immediate documentation of security incidents and critical decisions

### Validation Checklist
Before committing narrative updates:
- [ ] All dates are ISO 8601 format (YYYY-MM-DD)
- [ ] Decision IDs follow convention (DEC-YYYY-MMDD-###)
- [ ] All file paths are absolute (/home/setup/...)
- [ ] JSON validates: `python -m json.tool INFRAFABRIC_DECISION_TIMELINE.json`
- [ ] Links are current and point to existing files/commits
- [ ] Status values are from approved list
- [ ] Categories follow established conventions
- [ ] New entries link to related documentation

### Git Commit Message Template
```
Add narrative timeline entry: [Event Title] (YYYY-MM-DD)

- Subject: [Description]
- Category: [Category]
- Status: [Status]
- References: [Key files/commits]

Satisfies IF.TTT compliance requirement for Traceable project history.
```

---

## Compliance Notes

### IF.TTT (Traceable, Transparent, Trustworthy)
All entries in this directory support IF.TTT compliance:
- **Traceable:** Each decision links to source files, git commits, and documentation
- **Transparent:** All decision-making processes documented with participant lists
- **Trustworthy:** Status tracking and validation pipeline ensures accuracy

### Citation Standard
Decision timeline entries function as automatic citations (IF.citate) for all decisions and milestones in the project.

### Gemini Gold Standard
This directory satisfies Gold Standard requirements through:
- Comprehensive narrative documentation
- Machine-readable structured data
- Clear governance and decision traceability
- Linked evidence and supporting documentation

---

**Directory Status:** Active and maintained
**Last Updated:** 2025-11-26
**Maintainer:** IF.Librarian (InfraFabric Documentation System)
**Contact:** See `/home/setup/infrafabric/agents.md` for component contacts
