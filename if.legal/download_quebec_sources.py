#!/usr/bin/env python3
"""
Quebec Legal Sources Downloader for ContractGuard
Systematically downloads 65+ sources across 9 legal verticals
Bilingual support: FR (official) and EN (translations)
"""

import os
import sys
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/setup/if-legal-corpus/logs/download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuebecLegalDownloader:
    """Download Quebec legal sources with bilingual support"""

    def __init__(self):
        self.base_path = Path('/home/setup/if-legal-corpus/raw/quebec')
        self.log_path = Path('/home/setup/if-legal-corpus/logs')
        self.log_path.mkdir(exist_ok=True)

        # Statistics tracking
        self.stats = {
            'total_attempted': 0,
            'fr_success': 0,
            'en_success': 0,
            'bilingual_pairs': 0,
            'failed': 0,
            'total_mb': 0.0,
            'failed_sources': []
        }

        # Timeout for each request
        self.timeout = 15

        # User-Agent to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Sources to download organized by vertical
        self.sources = {
            'employment': [
                {
                    'name': 'Loi sur les normes du travail',
                    'en_name': 'Act respecting labour standards',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/n-1.1',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/n-1.1',
                    'cqlr': 'c N-1.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Code du travail du Québec',
                    'en_name': 'Labour Code',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/lc-1964/derniere/lc-1964.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-c-27/latest/cqlr-c-c-27.html',
                    'cqlr': 'c C-27',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur les accidents du travail et maladies professionnelles',
                    'en_name': 'Act respecting industrial accidents and occupational diseases',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/A-3.001',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/A-3.001',
                    'cqlr': 'c A-3.001',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur la santé et sécurité du travail',
                    'en_name': 'Act respecting occupational health and safety',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/S-2.1',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/S-2.1',
                    'cqlr': 'c S-2.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur l\'équité salariale',
                    'en_name': 'Pay Equity Act',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-e-12.001/derniere/rlrq-c-e-12.001.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-e-12.001/latest/cqlr-c-e-12.001.html',
                    'cqlr': 'c E-12.001',
                    'priority': 'P1'
                },
                {
                    'name': 'Charte des droits et libertés de la personne',
                    'en_name': 'Charter of Human Rights and Freedoms',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/C-12',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/c-12',
                    'cqlr': 'c C-12',
                    'priority': 'P0'
                }
            ],
            'ip': [
                {
                    'name': 'Code Civil du Québec - Book IV (Propriété)',
                    'en_name': 'Civil Code of Québec - Book IV (Property)',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991?section=871',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991?section=871',
                    'cqlr': 'c CCQ-1991 (Book IV)',
                    'priority': 'P1'
                },
                {
                    'name': 'Code Civil du Québec - Book V (Obligations)',
                    'en_name': 'Civil Code of Québec - Book V (Obligations)',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991?section=1371',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991?section=1371',
                    'cqlr': 'c CCQ-1991 (Book V)',
                    'priority': 'P1'
                },
                {
                    'name': 'Loi sur le droit d\'auteur (Federal)',
                    'en_name': 'Copyright Act (Federal)',
                    'fr_url': 'https://laws-lois.justice.gc.ca/fra/acts/c-42/',
                    'en_url': 'https://laws-lois.justice.gc.ca/eng/acts/c-42/',
                    'cqlr': 'R.S.C., 1985, c C-42',
                    'priority': 'P0'
                },
                {
                    'name': 'Marques de commerce et brevets (Fédéral)',
                    'en_name': 'Trademarks and Patents Act (Federal)',
                    'fr_url': 'https://laws-lois.justice.gc.ca/fra/lois/t-13/derniere/t-13.html',
                    'en_url': 'https://laws-lois.justice.gc.ca/eng/acts/t-13/',
                    'cqlr': 'R.S.C., 1985, c T-13',
                    'priority': 'P1'
                }
            ],
            'tax': [
                {
                    'name': 'Loi sur les impôts',
                    'en_name': 'Taxation Act',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/I-3',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/i-3',
                    'cqlr': 'c I-3',
                    'priority': 'P0'
                },
                {
                    'name': 'Regulation d\'application de la Loi sur les impôts',
                    'en_name': 'Regulation respecting the Taxation Act',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/cr/I-3,%20r%201',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cr/i-3,%20r.%201',
                    'cqlr': 'c I-3, r 1',
                    'priority': 'P1'
                },
                {
                    'name': 'Loi sur la taxe de vente du Québec',
                    'en_name': 'Act respecting the Québec Sales Tax (QST)',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/T-0.1',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/T-0.1',
                    'cqlr': 'c T-0.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur l\'administration fiscale',
                    'en_name': 'Tax Administration Act',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-a-6.002/derniere/rlrq-c-a-6.002.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-a-6.002/latest/cqlr-c-a-6.002.html',
                    'cqlr': 'c A-6.002',
                    'priority': 'P1'
                },
                {
                    'name': 'Loi concernant l\'impôt sur le tabac',
                    'en_name': 'Tobacco Tax Act',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/I-2',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/I-2',
                    'cqlr': 'c I-2',
                    'priority': 'P2'
                },
                {
                    'name': 'Revenu Québec Laws and Regulations',
                    'en_name': 'Revenue Quebec Laws and Regulations Portal',
                    'fr_url': 'https://www.revenuquebec.ca/fr/a-propos-de-nous/documents-administratifs-et-fiscaux/lois-et-reglements-administres-par-revenu-quebec/',
                    'en_url': 'https://www.revenuquebec.ca/en/about-us/administrative-and-tax-documents/laws-and-regulations-administered-by-revenu-quebec/',
                    'cqlr': 'Portal',
                    'priority': 'P1'
                }
            ],
            'property': [
                {
                    'name': 'Code Civil du Québec - Book IV (Property)',
                    'en_name': 'Civil Code of Québec - Book IV (Property)',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991?section=871',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991?section=871',
                    'cqlr': 'c CCQ-1991',
                    'priority': 'P0'
                },
                {
                    'name': 'Code Civil du Québec - Book V (Obligations)',
                    'en_name': 'Civil Code of Québec - Book V (Obligations)',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991?section=1371',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991?section=1371',
                    'cqlr': 'c CCQ-1991',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur les bureaux de la publicité des droits',
                    'en_name': 'Law on Registry Offices for the Publication of Rights',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-b-9/derniere/rlrq-c-b-9.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-b-9/latest/cqlr-c-b-9.html',
                    'cqlr': 'c B-9',
                    'priority': 'P0'
                },
                {
                    'name': 'Règlement sur la publicité foncière',
                    'en_name': 'Regulation on Land Publication',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/regl/rrq-c-b-9-r-4/derniere/rrq-c-b-9-r-4.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/regu/cqlr-c-b-9-r-6/latest/cqlr-c-b-9-r-6.html',
                    'cqlr': 'c CCQ, r 6',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi visant à moderniser certaines règles relatives à la publicité foncière',
                    'en_name': 'Law modernizing land publication rules',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/loisa/lq-2020-c-17/derniere/lq-2020-c-17.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/amending-acts/lq-2020-c-17/latest/lq-2020-c-17.html',
                    'cqlr': 'LQ 2020, c 17',
                    'priority': 'P1'
                },
                {
                    'name': 'Tarif des droits relatifs à la publicité foncière',
                    'en_name': 'Fee schedule for land publication',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/regl/rrq-c-b-9-r-1/derniere/rrq-c-b-9-r-1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/regu/cqlr-c-b-9-r-1/latest/cqlr-c-b-9-r-1.html',
                    'cqlr': 'c B-9, r 1',
                    'priority': 'P2'
                },
                {
                    'name': 'Registry Office Services Portal',
                    'en_name': 'Registraire des entreprises',
                    'fr_url': 'https://www.registreentreprises.gouv.qc.ca/fr/',
                    'en_url': 'https://www.registreentreprises.gouv.qc.ca/en/',
                    'cqlr': 'Portal',
                    'priority': 'P1'
                }
            ],
            'accounting': [
                {
                    'name': 'Loi sur les compagnies',
                    'en_name': 'Companies Act',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/C-38',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/c-38',
                    'cqlr': 'c C-38',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur les sociétés par actions',
                    'en_name': 'Business Corporations Act',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-s-31.1/derniere/rlrq-c-s-31.1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-s-31.1/latest/cqlr-c-s-31.1.html',
                    'cqlr': 'c S-31.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur la publicité légale des entreprises',
                    'en_name': 'Act respecting the legal publicity of enterprises',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/P-44.1',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/p-44.1',
                    'cqlr': 'c P-44.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Code des professions',
                    'en_name': 'Professional Code',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/C-26',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/c-26',
                    'cqlr': 'c C-26',
                    'priority': 'P1'
                },
                {
                    'name': 'Loi sur les comptables professionnels agréés',
                    'en_name': 'Chartered Professional Accountants Act',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-c-48.1/derniere/rlrq-c-c-48.1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-c-48.1/latest/cqlr-c-c-48.1.html',
                    'cqlr': 'c C-48.1',
                    'priority': 'P1'
                },
                {
                    'name': 'Code d\'éthique des comptables professionnels agréés',
                    'en_name': 'Code of ethics of chartered professional accountants',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/cr/C-48.1,%20r.%206',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cr/c-48.1,%20r.%206',
                    'cqlr': 'c C-48.1, r 6',
                    'priority': 'P2'
                },
                {
                    'name': 'Loi sur les sociétés d\'investissement du Québec',
                    'en_name': 'Act respecting Québec business investment companies',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-s-29.1/derniere/rlrq-c-s-29.1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-s-29.1/latest/cqlr-c-s-29.1.html',
                    'cqlr': 'c S-29.1',
                    'priority': 'P2'
                }
            ],
            'housing': [
                {
                    'name': 'Code Civil du Québec - Articles 1851-2000 (Lease)',
                    'en_name': 'Civil Code of Québec - Lease provisions',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991?section=1851',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991?section=1851',
                    'cqlr': 'c CCQ-1991',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur la Régie du logement (Tribunal administratif du logement)',
                    'en_name': 'Act respecting the Tribunal administratif du logement',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-r-8.1/derniere/rlrq-c-r-8.1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-r-8.1/latest/cqlr-c-r-8.1.html',
                    'cqlr': 'c R-8.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Tribunal administratif du logement Portal',
                    'en_name': 'Tribunal administratif du logement',
                    'fr_url': 'https://www.tal.gouv.qc.ca/fr/etre-locataire/droits-et-obligations-du-locataire',
                    'en_url': 'https://www.tal.gouv.qc.ca/en/being-a-tenant/rights-and-obligations-of-the-tenant',
                    'cqlr': 'Portal',
                    'priority': 'P1'
                }
            ],
            'insurance': [
                {
                    'name': 'Loi sur les assurances',
                    'en_name': 'Act respecting insurance',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/A-32',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/A-32',
                    'cqlr': 'c A-32',
                    'priority': 'P0'
                },
                {
                    'name': 'Regulation d\'application de la Loi sur les assurances',
                    'en_name': 'Regulation under the Act respecting insurance',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/cr/A-32.1,%20r%201',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cr/a-32.1,%20r.%201',
                    'cqlr': 'c A-32.1, r 1',
                    'priority': 'P1'
                },
                {
                    'name': 'Loi sur la distribution de produits et services financiers',
                    'en_name': 'Act respecting the distribution of financial products and services',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-d-9.2/derniere/rlrq-c-d-9.2.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-d-9.2/latest/cqlr-c-d-9.2.html',
                    'cqlr': 'c D-9.2',
                    'priority': 'P1'
                },
                {
                    'name': 'Code de déontologie de la Chambre de la sécurité financière',
                    'en_name': 'Code of ethics of the Chamber of Financial Security',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/regl/rrq-c-d-9.2-r-3/derniere/rrq-c-d-9.2-r-3.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/regu/cqlr-c-d-9.2-r-3/latest/cqlr-c-d-9.2-r-3.html',
                    'cqlr': 'c D-9.2, r 3',
                    'priority': 'P2'
                }
            ],
            'construction': [
                {
                    'name': 'Loi sur le bâtiment',
                    'en_name': 'Building Act',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-b-1.1/derniere/rlrq-c-b-1.1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-b-1.1/latest/cqlr-c-b-1.1.html',
                    'cqlr': 'c B-1.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Code de construction du Québec (2015)',
                    'en_name': 'Construction Code of Quebec (2015)',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/regl/rrq-c-b-1.1-r-2/derniere/rrq-c-b-1.1-r-2.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/regu/cqlr-c-b-1.1-r-2/latest/cqlr-c-b-1.1-r-2.html',
                    'cqlr': 'c B-1.1, r 2',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur les relations du travail, formation et main-d\'oeuvre en construction (R-20)',
                    'en_name': 'Act respecting labour relations in the construction industry',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/lrq-c-r-20/derniere/lrq-c-r-20.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/rsa-c-r-20/latest/rsa-c-r-20.html',
                    'cqlr': 'c R-20',
                    'priority': 'P0'
                },
                {
                    'name': 'Règlement d\'application de la Loi R-20',
                    'en_name': 'Regulation under Act R-20',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/regl/rlrq-c-r-20-r-1/derniere/rlrq-c-r-20-r-1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/regu/cqlr-c-r-20-r-1/latest/cqlr-c-r-20-r-1.html',
                    'cqlr': 'c R-20, r 1',
                    'priority': 'P1'
                },
                {
                    'name': 'Code Civil du Québec - Book V (Enterprise Contracts)',
                    'en_name': 'Civil Code of Québec - Enterprise Contracts',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991?section=2098',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/ccq-1991?section=2098',
                    'cqlr': 'c CCQ-1991 (Articles 2098-2230)',
                    'priority': 'P1'
                },
                {
                    'name': 'RBQ Portal - Construction Code and Safety',
                    'en_name': 'RBQ - Regulatory agency',
                    'fr_url': 'https://www.rbq.gouv.qc.ca/fr/lois-reglements-et-codes/code-de-construction-et-code-de-securite/code-de-construction/',
                    'en_url': 'https://www.rbq.gouv.qc.ca/en/laws-regulations-and-codes/construction-code-and-safety-code/construction-code/',
                    'cqlr': 'Portal',
                    'priority': 'P1'
                },
                {
                    'name': 'CCQ Portal - Construction Labour Relations',
                    'en_name': 'CCQ - Construction labour commission',
                    'fr_url': 'https://www.ccq.org/fr/loi-r20/relations-travail',
                    'en_url': 'https://www.ccq.org/en/loi-r20/relations-travail',
                    'cqlr': 'Portal',
                    'priority': 'P1'
                }
            ],
            'criminal': [
                {
                    'name': 'Code de procédure pénale du Québec',
                    'en_name': 'Code of Penal Procedure',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/C-25.1',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/C-25.1',
                    'cqlr': 'c C-25.1',
                    'priority': 'P0'
                },
                {
                    'name': 'Code criminel (Fédéral)',
                    'en_name': 'Criminal Code (Federal)',
                    'fr_url': 'https://laws-lois.justice.gc.ca/fra/acts/c-46/',
                    'en_url': 'https://laws-lois.justice.gc.ca/eng/acts/c-46/',
                    'cqlr': 'R.S.C., 1985, c C-46',
                    'priority': 'P0'
                },
                {
                    'name': 'Code de la sécurité routière',
                    'en_name': 'Highway Safety Code',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/C-24.2',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/C-24.2',
                    'cqlr': 'c C-24.2',
                    'priority': 'P0'
                },
                {
                    'name': 'Loi sur les infractions en matière de boissons alcooliques',
                    'en_name': 'Act respecting offences relating to alcoholic beverages',
                    'fr_url': 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/I-8.1',
                    'en_url': 'https://www.legisquebec.gouv.qc.ca/en/document/cs/I-8.1',
                    'cqlr': 'c I-8.1',
                    'priority': 'P1'
                },
                {
                    'name': 'Loi sur la Régie des alcools, des courses et des jeux',
                    'en_name': 'Act respecting the Régie des alcools, des courses et des jeux',
                    'fr_url': 'https://www.canlii.org/fr/qc/legis/lois/rlrq-c-r-6.1/derniere/rlrq-c-r-6.1.html',
                    'en_url': 'https://www.canlii.org/en/qc/laws/stat/cqlr-c-r-6.1/latest/cqlr-c-r-6.1.html',
                    'cqlr': 'c R-6.1',
                    'priority': 'P2'
                }
            ]
        }

    def download_source(self, url, filename, vertical):
        """Download a single source and calculate SHA-256"""
        try:
            logger.info(f"Downloading: {filename} from {url}")

            # Create request with headers
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read()

                # Save file
                file_path = self.base_path / vertical / filename
                with open(file_path, 'wb') as f:
                    f.write(content)

                # Calculate SHA-256
                sha256 = hashlib.sha256(content).hexdigest()

                # File size in MB
                size_mb = len(content) / (1024 * 1024)

                logger.info(f"Success: {filename} ({size_mb:.2f} MB, SHA256: {sha256[:16]}...)")

                return {
                    'status': 'success',
                    'filename': filename,
                    'size_mb': size_mb,
                    'sha256': sha256,
                    'url': url
                }

        except urllib.error.URLError as e:
            logger.error(f"URL Error downloading {filename}: {e}")
            return {'status': 'failed', 'filename': filename, 'error': str(e)}
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error {e.code} downloading {filename}")
            return {'status': 'failed', 'filename': filename, 'error': f"HTTP {e.code}"}
        except Exception as e:
            logger.error(f"Error downloading {filename}: {e}")
            return {'status': 'failed', 'filename': filename, 'error': str(e)}

    def run(self):
        """Main download process"""
        logger.info("="*80)
        logger.info("QUEBEC LEGAL SOURCES DOWNLOADER - ContractGuard")
        logger.info("="*80)
        logger.info(f"Start time: {datetime.now().isoformat()}")

        manifest = {
            'metadata': {
                'download_date': datetime.now().isoformat(),
                'total_verticals': len(self.sources),
                'source_count': sum(len(v) for v in self.sources.values())
            },
            'verticals': {}
        }

        # Download by vertical
        for vertical, sources in self.sources.items():
            logger.info(f"\n{'='*80}")
            logger.info(f"VERTICAL: {vertical.upper()}")
            logger.info(f"{'='*80}")

            vertical_results = []

            for source in sources:
                self.stats['total_attempted'] += 1

                # French version
                fr_filename = f"{source['name'].replace(' ', '_').lower()}-FR.md"
                fr_result = self.download_source(source['fr_url'], fr_filename, vertical)

                if fr_result['status'] == 'success':
                    self.stats['fr_success'] += 1
                    self.stats['total_mb'] += fr_result['size_mb']
                else:
                    self.stats['failed'] += 1
                    self.stats['failed_sources'].append({
                        'vertical': vertical,
                        'name': source['name'],
                        'language': 'FR',
                        'error': fr_result.get('error', 'Unknown')
                    })

                time.sleep(0.5)  # Rate limiting

                # English version
                en_filename = f"{source['name'].replace(' ', '_').lower()}-EN.md"
                en_result = self.download_source(source['en_url'], en_filename, vertical)

                if en_result['status'] == 'success':
                    self.stats['en_success'] += 1
                    self.stats['total_mb'] += en_result['size_mb']
                    self.stats['bilingual_pairs'] += 1
                else:
                    self.stats['failed'] += 1
                    self.stats['failed_sources'].append({
                        'vertical': vertical,
                        'name': source['name'],
                        'language': 'EN',
                        'error': en_result.get('error', 'Unknown')
                    })

                time.sleep(0.5)  # Rate limiting

                # Record in manifest
                vertical_results.append({
                    'source': source['name'],
                    'cqlr': source['cqlr'],
                    'priority': source['priority'],
                    'fr': fr_result,
                    'en': en_result
                })

            manifest['verticals'][vertical] = vertical_results

        # Save manifest
        manifest['summary'] = self.stats
        manifest_path = self.log_path / 'download_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        # Print summary
        self.print_summary()

        logger.info(f"\nEnd time: {datetime.now().isoformat()}")
        logger.info(f"Manifest saved to: {manifest_path}")

    def print_summary(self):
        """Print download summary"""
        logger.info("\n" + "="*80)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("="*80)
        logger.info(f"Total attempted:        {self.stats['total_attempted']}")
        logger.info(f"French successful:      {self.stats['fr_success']}")
        logger.info(f"English successful:     {self.stats['en_success']}")
        logger.info(f"Bilingual pairs:        {self.stats['bilingual_pairs']}")
        logger.info(f"Failed downloads:       {self.stats['failed']}")
        logger.info(f"Total MB downloaded:    {self.stats['total_mb']:.2f}")
        logger.info(f"Success rate:           {((self.stats['fr_success'] + self.stats['en_success']) / (self.stats['total_attempted'] * 2 if self.stats['total_attempted'] > 0 else 1) * 100):.1f}%")

        if self.stats['failed_sources']:
            logger.info("\nFailed sources:")
            for failed in self.stats['failed_sources']:
                logger.info(f"  - {failed['vertical']}/{failed['name']} ({failed['language']}): {failed['error']}")

if __name__ == '__main__':
    downloader = QuebecLegalDownloader()
    downloader.run()
