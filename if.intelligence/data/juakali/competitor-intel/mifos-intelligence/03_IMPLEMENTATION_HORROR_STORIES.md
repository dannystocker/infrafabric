SOURCE_CATEGORY: IMPLEMENTATION HORROR STORIES
RETRIEVED: 2025-12-03
CERTAINTY: MEDIUM-HIGH
DOCUMENT_COUNT: Forums, GitHub issues, Stack Overflow, mailing lists

# MIFOS/APACHE FINERACT - IMPLEMENTATION FAILURES & STRUGGLES

## DATA MIGRATION NIGHTMARES

### The Migration Pain Point (Direct Quote)

> "Data migration continues to be a **significant pain point** for MFIs moving on to Mifos."
> — Mifos developer mailing list

### Migration Complexity - The 90/10 Rule

**Conflux Technologies Report**:
> "Most of the **pain and effort resides in stage 1** (data cleansing and standardization). For Conflux, once the standard format (MS Access) and the scripts to push data into Mifos (VB scripts) are available, running the scripts is **no more than 5-10% of the total effort**."

**Translation**: 90-95% of migration effort is data cleanup. The "easy" part is only 5-10%.

### Manual Migration Nightmare

> "Manually migrating group data **cannot be done correctly** without modifying the system date where the application is running or by somehow modifying the data directly on the database after the group has being created and activated."
> — Mifos documentation

**Impact**: Requires either:
1. Dangerous system date manipulation
2. Direct database hacking
3. Neither is acceptable for production systems

### Migration Timeline Reality

**Example Project**:
- **Duration**: 2 weeks (with active MFI participation)
- **Process**: MFI personnel actively participated in cleansing activity
- **Testing**: Manual testing of migrated data with loan officer
- **Rollback**: Manual rollback required in case of errors

**Red Flag**: "Manual" everything - testing, rollback, verification

### The "Tons of Little Details" Problem

> "No major issues came up as problems, but there have been **tons of little details**...things like:
> - Fields we don't want to be mandatory that currently are
> - Not being able to disburse loans for a future date
> - Meeting schedules
>
> But we found a solution for all of them, **one by one**."
> — Implementation partner

**Translation**: Death by a thousand cuts. Every single issue requires workaround.

## INSTALLATION & SETUP FAILURES

### Ubuntu Installation Issues

**User Report**: "Issues on Ubuntu 18.04 during Step 4"

**Problem**: Running `sudo apt-get install npm nodejs-legacy`
**Error**: "Package nodejs-legacy is not available"

**Impact**: Installation guide doesn't match current Ubuntu versions. Dead in the water.

### FFI Gem Installation Failure

**Error**: "An error occurred while installing ffi (1.15.3), and Bundler cannot continue."

**Impact**: Cannot complete Ruby dependencies installation. Installation blocked.

### Pentaho Reports Directory Missing

**Problem**: If `/pentahoReports` not copied into `/root/.mifosx`, accounting reports fail

**Error**: "Unable to create key" for report files

**Impact**:
- Accounting reports broken
- Non-obvious error message
- Requires deep technical knowledge to diagnose
- Common mistake in installations

### ClassNotFoundException Horror

**Error**: "ClassNotFoundException org.apache.catalina.core.JasperListener"

**Fix**: Manually remove corresponding line from server.xml

**Impact**: Requires editing Tomcat configuration files. Not for the faint of heart.

### The Credentials Confusion

**User Report - Stack Overflow**:
> "I have tried installing Mifos X on XAMPP. It's worked as I could access the UI on my browser but **I had lots of problems with the credentials**"

**Problem**: Setting MySQL passwords differently from suggested defaults breaks everything

**Impact**: Documentation assumes specific passwords. Deviation = failure.

## API & BACKEND NIGHTMARES

### Version 1.12.1 API Failure

**User Report**: "Fineract API not running on localhost:8080"

**Details**:
- Works with version 1.11.0
- Fails with 1.12.1 release candidate
- No clear explanation why

**Impact**: Upgrade breaks API. Stuck on old version.

### Version 1.12.0 Complete Failure

**Official Statement**:
> "Version 1.12.0 had **build+test issues and was discarded**. Users are recommended to use 1.12.1 instead."

**Impact**: Entire release version unusable. If you deployed 1.12.0, start over.

### The 404 Error Mystery

**User Report**: "App receives 404 errors while trying to access the backend at https://ip:8443/fineract-provider"

**Context**: Following official installation guide for Ubuntu 20.04 server

**Impact**: Complete connection failure between frontend and backend. System non-functional.

### Pentaho + Gradle Compilation Failure

**Problem**: Missing Pentaho Reporting Engine packages when building with Gradle

**Impact**:
- Cannot compile project
- Requires manual dependency resolution
- Not documented clearly

## CONFIGURATION HELL

### Fineract CN Missing Properties

**Problem**: Following Fineract CN setup guide, encounter missing properties:
- `fin.keycloak.realm.publicKey`
- `keycloak.auth-server-url`
- Other Keycloak-related configurations

**Impact**:
- Cannot run Postman scripts
- Authentication setup fails
- Stuck at initial setup

**Context**: This is following the OFFICIAL setup guide

### Self-Signed Certificate Nightmare

**Problem**: Apache Fineract uses self-signed certificates

**User Experience**:
- Must manually open https://localhost:8443/fineract-provider/
- Must accept certificate in browser
- Must do this BEFORE logging in via UI
- Browser warnings confuse users

**Impact**:
- Poor user experience
- Security warnings alarm users
- Mobile apps fail to connect
- Requires expensive SSL certificate for production

## MOBILE APP DISASTERS

### Demo Credentials Don't Work

**Issue #2665 (August 2024)**: Demo credentials not working, login issues

**Impact**:
- New users can't even try the demo
- First impression = failure
- 124 open issues on mobile repo

### Login Error - API Version Mismatch

**User Report**:
> "Receiving 'Invalid Authentication details where Passed in API request' error when trying to login to Mifos Mobile app"

**Root Cause**:
- Latest Fineract version has problems receiving requests from apps
- Web-Self service app can ONLY connect to MifosX Release 18.03.01 and 17.07.01
- Changes in latest build MifosX 21.07.01 broke compatibility

**Impact**:
- App can't connect to latest backend
- Forced to use old backend versions
- Security vulnerabilities in old versions
- Catch-22 situation

### The API Endpoint Apocalypse

**Problem**: Mifos X Android app pointing to old API endpoint `https://[ip]/mifosng-provider/api/v1`

**Impact**:
- Users who upgraded to Fineract platform = broken app
- Field agents can't use application
- Invested gadgets (tablets, phones) = useless

**User Quote**:
> "This is a major issue affecting many MFIs whose field agents couldn't use the application, **rendering their invested gadgets unusable**."

### App Freezing on Transactions

**Problem**: App freezes whenever users make savings withdrawal or deposit

**Impact**:
- Core functionality broken
- Cannot process transactions
- Field operations disrupted

### App Crashing After PIN Entry

**Problem**: App crashes after entering PIN correctly, even with active internet connection

**Impact**:
- Cannot access app
- Authentication works but app fails
- No error message to help diagnose

## PENTAHO REPORTING DISASTERS

### Parameter Configuration Data Integrity Issue

**Common Error**: "parameterName":null,"value": null,"args"

**Cause**: Parameter provided in SQL query but not configured in Mifos - Create report

**Impact**:
- Reports fail to run
- Non-obvious error message
- Requires understanding of both SQL and Mifos configuration
- "Data integrity" error is misleading

### Version Compatibility Hell

**Problem**: "Due to updates of a number of dependencies, it's not possible to run pentaho reports with certain version combinations"

**Impact**:
- Working reports suddenly break after upgrade
- Must match exact Pentaho version to Mifos version
- Pentaho 3.9.1-GA recommended but may not work with all versions
- Trial and error to find compatible versions

### MySQL Strict Mode Breaks Reports

**Problem**: MySQL version comes with preset conditions that break Pentaho reports

**Workaround**: Create `/etc/mysql/conf.d/disable_strict_mode.cnf` with custom sql_mode settings

**Impact**:
- Requires MySQL server configuration changes
- Must disable security features
- Not documented in main installation guide
- Database administrator knowledge required

### Report Parsing Failures

**Problem**: "Pentaho reports cannot be parsed successfully" when running accounting reports

**Impact**:
- Accounting reports completely broken
- No financial reporting
- Audit nightmare
- Compliance issues

### The Missing Logo Error

**Error**: "Unable to create key: No loader was able to handle the given key data" for MIfosX_unofficial_logo.png

**Cause**: Path isn't correct

**Workaround**: Manually place logo inside pentahoReports folder with exact filename

**Impact**:
- Reports fail for missing image
- Cryptic error message
- Requires file system manipulation
- Easy to miss in setup

### Blank Page of Death

**User Report**: "Successfully installed Mifos but when running pentaho reports get a blank page"

**Cause**: "Application is returning the Pentaho report, but UI is not showing the output"

**Impact**:
- Reports generated but not visible
- Backend works, frontend fails
- No error message
- Appears to be working but isn't

## UPGRADE & MIGRATION HORRORS

### Failed Upgrade Error

**Error**: "Migration of schema failed!" during Mifos X upgrade

**Required Steps**:
1. Stop Tomcat server
2. Manual database intervention
3. Restart
4. Pray

**Impact**: Upgrade process is dangerous and can brick the system

### The Flyway to Liquibase Migration

**Major Breaking Change**:
- Flyway used until Fineract 1.6.x
- Liquibase required from 1.7.0 onwards
- PostgreSQL support added, requiring database-independent migration

**Impact**:
- Cannot directly upgrade from pre-1.6 to post-1.7
- Must go through 1.6.0 as intermediate step
- Migration scripts may not run
- Manual intervention required

### Unique Constraint Name Mismatch

**Specific Issue FINERACT-1930**: Migration script 0016_changed_unique_constraint_of_ref_no.xml failed while migrating from 1.6.0 to 1.8.4

**Cause**: Mismatch of unique constraint name in m_savings_account_transaction table

**Impact**:
- Upgrade blocked
- Requires manual database schema inspection
- Must manually fix constraint names
- High risk of data corruption

### MariaDB Upgrade Failure

**Problem**: "Upgrading database from MySQL 5.7 as advised to Maria DB 10.6, fails"

**Details**:
- Data from version 18.03.01 fails to migrate
- Databases running on 1.5.0 release complete startup BUT login fails

**Impact**:
- Stuck on old database version
- Cannot follow upgrade recommendations
- Security vulnerabilities in old MySQL versions

### Timezone Hell

**Problem**: "If a previously used Fineract instance didn't run in UTC (backward compatibility), all prior dates will be read wrongly by MySQL"

**Impact**:
- Database migration scripts produce incorrect data
- Historical data corrupted
- Loan schedules calculated incorrectly
- Financial reporting inaccurate

### Intermittent Build Failures After Upgrade

**User Report**: "We recently migrated our application from Fineract 1.4 to Fineract 1.9. After addressing all conflicts and successfully executing migration scripts, application is running smoothly without functional issues. **However**, intermittent issue during build process."

**Details**: Failures typically related to Fineract Avro dependencies

**Impact**:
- Unpredictable build failures
- Deployment delays
- CI/CD pipeline broken
- Developer frustration

## PERFORMANCE NIGHTMARES

### Single-Threaded Scheduler

**Problem**: "The scheduler jobs are single threaded, meaning no two jobs can be executed parallelly"

**Impact**:
- Performance bottleneck
- Jobs queue up
- Batch processing slow
- Overnight jobs may not complete

### The Query That Takes Forever

**Problem**: "For a large organization containing millions of transactions, for the defined period set the backend processing query **takes forever to complete** the processing"

**Impact**:
- Reports timeout
- UI becomes unresponsive
- Users think system crashed
- Operational paralysis

### HTTP 413 Payload Too Large

**Problem**: "For field app users to gain access to large set of data, owing to size of http response body '413 Payload Too Large' errors could occur"

**Impact**:
- Cannot sync field data
- Mobile app broken for large datasets
- Field operations disrupted
- Data usage "considerably high"

## COLLECTION SHEET DEPRECATION CONTROVERSY

### The Microfinance Abandonment

**Community Member Quote (August 2024)**:
> "The influx of new features in Fineract is that these are predominantly **not for microfinance or small entities, which Mifos once set out to support**. [We] see the deprecation of the Collection Sheet feature in this context."

**Implication**: Apache Fineract moving away from microfinance focus

**Mifos Response**:
> "Regardless of what decision the Fineract community makes in regards to deprecation of collection sheet functionality, **Mifos will not be removing this functionality** nor diminishing its focus on microfinance and financial inclusion within the Mifos X distribution."

**Impact**:
- Split between Fineract and Mifos directions
- Uncertainty about future features
- Core microfinance functionality at risk
- Must rely on Mifos Initiative, not Apache

## STACK OVERFLOW CRY FOR HELP

### Top Questions Reveal Pain Points

1. **"Run/Debug Apache Fineract using Eclipse?"**
   - Answer: "Only way is running embedded Gradle task and attaching remote debugger"
   - Translation: Debugging is a nightmare

2. **"Fineract CN Basic Setup"**
   - Missing Keycloak properties
   - Cannot complete basic setup
   - Following official guide

3. **"Combining Fineract on backend and mifos UI on front end"**
   - Users struggle to connect UI to backend
   - Should be straightforward but isn't
   - Errors when integrating

4. **"How to create moratorium loan in apache finaract"**
   - Repayment schedule doesn't show correct interest
   - Even with 6-month grace periods configured
   - Core loan functionality broken

5. **"Apache Fineract Reporting"**
   - Must manually add PentahoReportingProcessServiceImpl
   - Add Pentaho dependencies to dependencies.gradle
   - Why isn't this automatic?

6. **"Fineract does not ship Pentaho reports or related libraries due to Apache license compliance issues"**
   - Legal issues prevent including key functionality
   - Users directed to "Mifos community for distributions"
   - Fragmented solution

## THE REAL COST ADMISSION

### Infrastructure Costs (From FAQ)

> "On the infrastructure side, costs will include:
> - Connectivity
> - PCs
> - Power supplies at the branches
> - In on-site: cost of server and infrastructure at head office
> - In hosted: monthly hosting costs"

### Personnel Requirements

> "In addition to a **dedicated internal IT person** or an **external IT consultant or Mifos Specialist**, time will be needed from operational and business decision makers to configure and implement the system in alignment with the organization's business processes."

**Translation**: "Free" software needs:
- Dedicated IT staff OR expensive consultants
- Ongoing operational staff time
- Infrastructure investment
- Monthly hosting fees

### Implementation Timeline

> "On average a deployment takes **several months**"

**Factors affecting timeline**:
- Size of MFI
- Existing technical knowledge of staff
- Complexity of requirements

**Translation**: 3-6+ months to go live, assuming no major issues

## SOURCES
- https://groups.google.com/g/mifosusers/c/96Xy0Pmyh1k/m/udARdka2A3AJ
- https://mifosforge.jira.com/wiki/spaces/docs/pages/97615907/Failed+Upgrade+Tips+Mifos+X
- https://groups.google.com/g/mifosdeveloper/c/Vjm--R48iw8
- https://stackoverflow.com/questions/tagged/apache-fineract
- https://stackoverflow.com/questions/tagged/mifos
- https://github.com/openMF/mifos-mobile/issues/837
- https://github.com/openMF/mifos-mobile/issues/1191
- https://github.com/openMF/mifos-mobile/issues/2665
- https://groups.google.com/g/mifosusers/c/Edmr535yIu0
- https://docs.mifos.org/mifosx/user-manual/for-administrators-mifos-x-platform/initial-system-set-up
- https://mifosforge.jira.com/wiki/spaces/docs/pages/74711072/Mifos+X+Installation+on+Linux+-+Ubuntu+Server
- https://issues.apache.org/jira/browse/FINERACT-1930
- https://www.mail-archive.com/dev@fineract.apache.org/msg10991.html
- https://www.mail-archive.com/dev@fineract.apache.org/msg11200.html
