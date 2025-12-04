SOURCE_CATEGORY: PRODUCT INTELLIGENCE
RETRIEVED: 2025-12-03
CERTAINTY: HIGH
DOCUMENT_COUNT: Multiple sources consolidated

# MIFOS/APACHE FINERACT - PRODUCT OVERVIEW

## PRODUCT ARCHITECTURE

### Core Components
- **Apache Fineract**: Backend platform (APIs and business logic only, no UI)
  - Licensed under Apache License 2.0
  - Written primarily in Java
  - Donated to Apache Software Foundation by Mifos Initiative in December 2015
  - Graduated to top-level Apache project in April 2017

- **Mifos X**: Complete distribution built on Apache Fineract
  - Includes web app (community app), mobile apps, reporting tools (Pentaho)
  - Data import tools
  - Mobile app for field officers
  - Client mobile banking app (in development)
  - Full out-of-the-box solution for financial inclusion

### Technical Architecture
- Multitenant, service-oriented, tiered architecture
- Can be deployed as SaaS or on-premises
- CQRS (Command Query Responsibility Segregation) design pattern
- Service Layer with horizontal (services, command, event handlers) and vertical (functional modules) layers
- Role-based access control
- XBRL compliant reporting engine

### API Structure
- RESTful APIs grouped in modules
- Swagger documentation available at https://localhost:8443/fineract-provider/swagger-ui/index.html
- Full API documentation: https://demo.mifos.io/api-docs/apiLive.htm

## KEY FEATURES AND MODULES

### Core Banking Modules
1. **Client/Group Management**
   - Individual and group lending support
   - Address module (optional, configurable)

2. **Loan Products**
   - Declining balance interest calculation
   - Flat interest calculation
   - Interest recalculation capabilities
   - Progressive loan module
   - Moratorium loan support
   - Multiple repayment strategies

3. **Savings Products**
   - Interest calculations for deposit products
   - Fixed deposits with rollover

4. **Accounting**
   - Double-entry bookkeeping
   - Chart of Accounts (5 categories: Assets, Liabilities, Income, Expense, Equity)
   - General Ledger
   - Automated journal entries
   - Provisioning entries

5. **Additional Features**
   - Data import tool
   - SMS campaigns
   - Pentaho reports
   - Maker-Checker functionality (approval workflows)
   - Standing instructions

### Mobile Applications
- **Mifos X Android Client** (Field Officer app)
  - Available on Google Play Store
  - 124 open issues, 920 closed issues (as of 2024)

- **Mifos Mobile** (Client banking app)
  - Repository: https://github.com/openMF/mifos-mobile

## DEPLOYMENT SCALE

### Global Reach
- **20+ million customers** served worldwide
- **400+ financial institutions** using the platform
- **41+ countries** with active deployments
- **100+ deployment partners** globally
- **Hundreds of volunteers** contributing

### Example Deployments
- Grameen Koota (India): 450,000 clients, $5M USD ROI
- enda inter-arabe (Tunisia): 135,000 clients, $1.3M USD ROI
- Al Majmoua (Lebanon): Expected $840K USD ROI over 5 years
- Musoni Services: 100 financial institutions across Uganda, Tanzania, Kenya

### Notable MFI Sizes Using Mifos
- As small as 25 clients
- As large as 450,000 clients
- Battle-tested: 1.8 million existing active loans, 135,822 new loans processed

## DEVELOPMENT COMMUNITY

### GitHub Statistics (OpenHub data)
- **4,231 commits** by **104 contributors**
- **282,319 lines of code**
- **74 years** of estimated development effort (COCOMO model)
- First commit: April 2012
- Primary language: Java

### Organization
- **Mifos Initiative**: U.S.-based 501(c)3 non-profit founded October 2011
- **Mifos employees**: ~50
- **Apache Fineract**: Independent Apache Software Foundation project

### Active Development Programs
- **Google Summer of Code 2024**: 11 interns
- **Code for GovTech 2024**: 7 interns
- Total 18 interns working on Fineract backend, web/mobile apps, Payment Hub EE

## PROJECT HISTORY

### Timeline
- **2002**: Project originally created by James Dailey
- **2004**: Development began as Grameen Foundation initiative
- **2006**: Launched as open-source software Mifos
- **2011**: MifosX release; Grameen Foundation transitions to Mifos Initiative
- **2015**: Mifos X platform contributed to Apache Software Foundation
- **2017**: Apache Fineract graduates to top-level Apache project
- **2024**: Active development continues with version 1.10.1 released Dec 31, 2024

### Name Origin
"Mifos" originally stood for "Micro Finance Open Source" but is now used as a brand rather than an acronym.

## FORK ANALYSIS: APACHE FINERACT VS MIFOS X

### Relationship
- Apache Fineract = Core backend platform (no UI)
- Mifos X = Value-added distribution built on Fineract with UI, mobile apps, reports

### Other Distributions
- **Musoni System**: Built on Fineract, used by 100+ FIs across 15 countries
- **Finflux**: Provided by Conflux Technologies
- Multiple other commercial distributions exist

### Repository Status
- Main Mifos X repo (https://github.com/openMF/mifosx): DEPRECATED
- Main platform repo: https://github.com/apache/fineract
- Mifos continues to maintain value-added components at https://github.com/openMF

## LICENSING AND COST MODEL

### Software Licensing
- Apache License 2.0 (permissive open source)
- No licensing fees
- Goal: "Deployable with effectively no cost"

### Real Costs
1. **Infrastructure**: Servers, connectivity, PCs, power supplies at branches
2. **Hosting**: Monthly costs if cloud-hosted
3. **Personnel**: Dedicated IT person or external consultant/Mifos Specialist
4. **Implementation**: Services from deployment partners
5. **Training**: Staff training on system usage
6. **Customization**: Development costs for specific requirements

### Partner Business Model
- Partners build viable businesses deploying Mifos and providing services
- Multi-tenant architecture ideal for cloud hosting
- Support, maintenance, hosting, training all revenue opportunities
- No centralized Mifos pricing; partners set their own rates

## SOURCES
- https://docs.mifos.org/mifosx/master
- https://docs.mifos.org/mifosx/developer-space/how-mifosx-works
- https://demo.mifos.io/api-docs/apiLive.htm
- https://github.com/openMF
- https://openhub.net/p/mifosx
- https://mifos.org/mifos-x/
- https://fineract.apache.org/
- https://mifos.org/blog/infrastructure-apache-mifosx/
- https://docs.mifos.org/overview-and-background/mifos-v-s-fineract
- https://en.wikipedia.org/wiki/Mifos_Initiative
- https://mifos.org/blog/gsoc-c4gt-2024/
- https://mifos.org/blog/documenting-technology-impact-mifos-roi-model-case-studies/
