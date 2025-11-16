# TEMPLATES & WORKFLOWS OPÉRATIONNELS
## Gedimat - Sondages + Communication Préventive Retards
### Documentation Technique pour Implémentation

---

## PARTIE A : TEMPLATES SONDAGES SATISFACTION

### TEMPLATE 1 : Sondage CSAT Post-Livraison (5 Questions - 2 min)

**CONTEXTE D'UTILISATION :**
- Déclenché : 48h après confirmation livraison client
- Canal : Email automatisé + SMS relance (J+7 pour non-répondants)
- Population : 100% commandes (24,000 sondages/an)
- Taux réponse cible : 50-55%
- Responsable setup : IT/Marketing

---

#### Version Email HTML (À adapter à template email)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: Arial, sans-serif; color: #333; }
  .container { max-width: 600px; margin: 0 auto; padding: 20px; }
  .header { background: #0066cc; color: white; padding: 20px; border-radius: 5px; }
  .question { margin: 20px 0; padding: 15px; border-left: 4px solid #0066cc; }
  .rating { font-size: 24px; margin: 10px 0; }
  .button { background: #ff6600; color: white; padding: 12px 24px;
            border: none; border-radius: 5px; cursor: pointer; }
  .footer { font-size: 12px; color: #999; margin-top: 30px; }
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <h1>⭐ Merci ! Votre avis en 2 min nous aide énormément</h1>
    <p>Commande #${ORDER_REF} livrée le ${DELIVERY_DATE}</p>
  </div>

  <p>Bonjour ${FIRST_NAME},</p>

  <p>Nous venons de livrer votre commande. <strong>Partagez votre avis en 2 minutes</strong> -
  tous les répondants participent à notre tirage <strong>100€ de bon d'achat</strong> ! 🎁</p>

  <form action="${FORM_ENDPOINT}" method="POST">

    <!-- QUESTION 1 : CSAT GLOBAL -->
    <div class="question">
      <h3>❓ QUESTION 1</h3>
      <p><strong>Comment jugez-vous votre expérience de livraison Gedimat ?</strong></p>
      <div class="rating">
        <input type="radio" name="q1_csat" value="5" required> <label>⭐⭐⭐⭐⭐ Très satisfait</label><br>
        <input type="radio" name="q1_csat" value="4"> <label>⭐⭐⭐⭐ Satisfait</label><br>
        <input type="radio" name="q1_csat" value="3"> <label>⭐⭐⭐ Neutre</label><br>
        <input type="radio" name="q1_csat" value="2"> <label>⭐⭐ Insatisfait</label><br>
        <input type="radio" name="q1_csat" value="1"> <label>⭐ Très insatisfait</label>
      </div>
    </div>

    <!-- QUESTION 2 : CES / FRICTION -->
    <div class="question">
      <h3>❓ QUESTION 2</h3>
      <p><strong>Avez-vous trouvé FACILE de commander et accéder à votre commande ?</strong></p>
      <div class="rating">
        <input type="radio" name="q2_ces" value="5" required> <label>Très facile 🚀</label><br>
        <input type="radio" name="q2_ces" value="4"> <label>Plutôt facile</label><br>
        <input type="radio" name="q2_ces" value="3"> <label>Neutre</label><br>
        <input type="radio" name="q2_ces" value="2"> <label>Plutôt difficile</label><br>
        <input type="radio" name="q2_ces" value="1"> <label>Très difficile 😞</label>
      </div>
      <p id="q2_follow" style="display:none; margin-top: 10px;">
        <label>Si difficile, qu'aurait pu être amélioré ?</label><br>
        <textarea name="q2_comment" rows="2" style="width: 100%; padding: 8px;"></textarea>
      </p>
      <script>
        document.querySelectorAll('input[name="q2_ces"]').forEach(radio => {
          radio.addEventListener('change', () => {
            document.getElementById('q2_follow').style.display =
              (radio.value <= 2) ? 'block' : 'none';
          });
        });
      </script>
    </div>

    <!-- QUESTION 3 : DÉLAI (CRITÈRE BTP) -->
    <div class="question">
      <h3>❓ QUESTION 3 ⏰</h3>
      <p><strong>Avez-vous reçu votre commande DANS LES DÉLAIS CONVENUS ?</strong></p>
      <div class="rating">
        <input type="radio" name="q3_delai" value="5" required> <label>✅ Oui, conforme délai</label><br>
        <input type="radio" name="q3_delai" value="4"> <label>Oui, légèrement en retard (+1-2j)</label><br>
        <input type="radio" name="q3_delai" value="1"> <label>❌ Retard significatif</label>
      </div>
      <p id="q3_follow" style="display:none; margin-top: 10px;">
        <label><input type="checkbox" name="q3_impact"> Cela a impacté mon chantier</label><br>
        <textarea name="q3_detail" rows="2" placeholder="Quel impact exact ?" style="width: 100%; padding: 8px;"></textarea>
      </p>
      <script>
        document.querySelectorAll('input[name="q3_delai"]').forEach(radio => {
          radio.addEventListener('change', () => {
            document.getElementById('q3_follow').style.display =
              (radio.value <= 1) ? 'block' : 'none';
          });
        });
      </script>
    </div>

    <!-- QUESTION 4 : NPS / FIDÉLITÉ -->
    <div class="question">
      <h3>❓ QUESTION 4 🤝</h3>
      <p><strong>Recommanderiez-vous Gedimat à un confrère/artisan ?</strong></p>
      <p style="font-size: 12px; color: #999;">0 = Pas du tout | 10 = Certainement</p>
      <div class="rating" style="display: flex; gap: 5px; justify-content: space-between;">
        <input type="radio" name="q4_nps" value="10" required style="display: none;">
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="10"> 10
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="9"> 9
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="8"> 8
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="7"> 7
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="6"> 6
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="5"> 5
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="4"> 4
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="3"> 3
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="2"> 2
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="1"> 1
        </label>
        <label style="cursor: pointer; padding: 5px 8px; background: #eee; border-radius: 3px;">
          <input type="radio" name="q4_nps" value="0"> 0
        </label>
      </div>
      <p id="q4_follow" style="display:none; margin-top: 10px;">
        <label><strong>Qu'améliorerions-nous d'urgent ?</strong></label><br>
        <textarea name="q4_comment" rows="2" style="width: 100%; padding: 8px;"></textarea>
      </p>
      <script>
        document.querySelectorAll('input[name="q4_nps"]').forEach(radio => {
          radio.addEventListener('change', () => {
            document.getElementById('q4_follow').style.display =
              (radio.value <= 6) ? 'block' : 'none';
          });
        });
      </script>
    </div>

    <!-- QUESTION 5 : SEGMENTATION -->
    <div class="question">
      <h3>❓ QUESTION 5 💡</h3>
      <p><strong>Avez-vous BESOIN DE → ? (Sélectionner 1-2 max)</strong></p>
      <div>
        <label><input type="checkbox" name="q5_needs" value="isolation"> Isolation / Étanchéité</label><br>
        <label><input type="checkbox" name="q5_needs" value="quincaillerie"> Quincaillerie / Outils</label><br>
        <label><input type="checkbox" name="q5_needs" value="peinture"> Peintures / Revêtements</label><br>
        <label><input type="checkbox" name="q5_needs" value="conseil"> Conseil technique (devis)</label><br>
        <label><input type="checkbox" name="q5_needs" value="livraison_express"> Livraison express</label><br>
        <label><input type="checkbox" name="q5_needs" value="none"> Pas de besoin particulier</label>
      </div>
    </div>

    <div style="text-align: center; margin-top: 30px;">
      <button type="submit" class="button">✅ ENVOYER MA RÉPONSE (2 min)</button>
    </div>

    <div class="footer">
      <p>Merci pour vos 2 minutes précieuses ! Tous les répondants participent au tirage 100€.</p>
      <p>Besoin d'aide immédiate ?
        <a href="tel:${SUPPORT_PHONE}">Appelez-nous</a> |
        <a href="mailto:${SUPPORT_EMAIL}">support@gedimat.fr</a>
      </p>
    </div>

  </form>

</div>

</body>
</html>
```

---

#### Version Simple Email Text (Fallback)

```
Sujet : ⭐ Votre avis en 2 minutes - Gedimat

Bonjour ${FIRST_NAME},

Merci de votre commande #${ORDER_REF} (livrée le ${DELIVERY_DATE}).

Partagez votre avis en 2 minutes → Tirez 100€ de bon d'achat ! 🎁

Répondre au sondage → [LIEN CLIQUABLE]

────────────────────────────────────────────────────────

Q1 : Êtes-vous satisfait de votre expérience Gedimat ?
  ☐ Très satisfait  ☐ Satisfait  ☐ Neutre  ☐ Insatisfait

Q2 : Avez-vous trouvé facile de commander ?
  ☐ Très facile  ☐ Plutôt facile  ☐ Neutre  ☐ Difficile

Q3 : Avez-vous reçu dans les délais convenus ?
  ☐ Oui  ☐ Légèrement en retard  ☐ Retard significatif

Q4 : Recommanderiez-vous Gedimat ? (0-10)
  [Slider ou saisie numérique]

Q5 : Avez-vous besoin de ?
  ☐ Isolation  ☐ Quincaillerie  ☐ Peinture  ☐ Conseil tech

────────────────────────────────────────────────────────

Répondre → [LIEN]

Merci, L'équipe Gedimat
```

---

### TEMPLATE 2 : Sondage NPS Annuel (2 questions - 1 min)

**CONTEXTE :**
- Fréquence : 1x/an (janvier ou juillet)
- Population : Panel 150-200 clients qualifiés
- Format : Email court ou call téléphonique rapide

```
Sujet : Gedimat 2025 - Votre fidélité compte pour nous 🤝

Bonjour ${FIRST_NAME},

En fin d'année, nous demandons à nos meilleurs clients :

**Q1 - Avec quelle probabilité recommanderiez-vous Gedimat à un confrère ?**

Répondre (10 secondes) → [0-10 Scale Link]

**Q2 - Qu'est-ce que nous pourrions améliorer d'urgent ?**

(Champ libre 200 caractères max)

────────────────────────────────────────────────────────

Répondre au sondage NPS → [LIEN]

Merci de votre fidélité,
L'équipe Gedimat
```

---

## PARTIE B : WORKFLOWS COMMUNICATION PRÉVENTIVE RETARDS

### WORKFLOW 1 : Détection Retard + SMS Alerte (Urgence 9-10)

**DÉCLENCHEUR :** Retard détecté >24h sur commande urgence 9-10
**TIMING :** J-2 avant date promise (exemple : mercredi 9h pour livraison prévue vendredi)
**CANAL :** SMS + Email + Appel téléphonique (VIP)

---

#### Scénario : Jean, artisan électricien Toulouse - Commande Urgente

```
DONNÉES COMMANDE :
- Ref : #1234
- Client : Jean ROUSSEAU
- Montant : 3,500€
- Délai promis : Vendredi 17h
- Délai estimé réel : Jeudi (J-1)
- Urgence score : 10 (RUSH - chantier lundi matin)
- Produit : Isolant 200m² + quincaillerie
- Contact : 06-12-34-56-78 | jean@rousseau-electricité.com

DÉTECTION : Mercredi 9h → Retard >24h détecté

═════════════════════════════════════════════════════════════

ÉTAPE 1 : SMS IMMÉDIAT (Mercredi 9h15)

Message SMS :
"🚨 Gedimat Alert - Cmd #1234
Livraison JEUDI 15h (pas vendredi)
Options: [1] Retrait mercredi 17h Dépôt
[2] Livraison express +50€
Confirmez : https://gedimat.click/cmd1234
Support 24h : 05-XX-XX-XX"

Approx 158 caractères → Envoyé automatiquement

═════════════════════════════════════════════════════════════

ÉTAPE 2 : EMAIL DÉTAIL (Immédiat après SMS)

De : noreply@gedimat.fr
À : jean@rousseau-electricité.com
Objet : ⚠️ IMPORTANT #1234 - Commande Gedimat - Retard Détecté

Bonjour Jean,

Nous vous contactons car votre commande #1234 (Isolant + Quincaillerie)
connait un léger RETARD en raison de [charge transport / cause generic].

📋 BONNE NOUVELLE : Nous vous proposons 3 solutions !

┌────────────────────────────────────────────────────────────┐
│ OPTION 1 : RETRAIT ACCÉLÉRÉ MERCREDI 17h                 │
├────────────────────────────────────────────────────────────┤
│ Lieu : Dépôt Gedimat Toulouse (Rue de Toulouse)          │
│ Horaire : Mercredi 16h-18h (accès direct, pas d'attente) │
│ Gain : -24h avant date prévue                             │
│ Coût : GRATUIT                                             │
│ ✅ Confirmer retrait → [LIEN]                             │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ OPTION 2 : LIVRAISON EXPRESS JEUDI MATIN                 │
├────────────────────────────────────────────────────────────┤
│ Créneau : Jeudi 08h-12h à votre adresse de chantier      │
│ Coût : +50€ (PRIS EN CHARGE PAR GEDIMAT pour cmd >2000€) │
│ Avantage : Reçu avant chantier lundi                      │
│ ✅ Accepter livraison express → [LIEN]                    │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ OPTION 3 : PRODUIT ALTERNATIF IN STOCK DEMAIN            │
├────────────────────────────────────────────────────────────┤
│ Produit : Isolant MARQUE X (qualité équivalente)         │
│ Bénéfice : -50€ sur commande (~100€ économies au total)  │
│ Délai : Livraison jeudi matin (conf. option 2)           │
│ Échange possible : Jusqu'à 10 jours (sans frais)         │
│ ✅ Accepter échange → [LIEN]                              │
└────────────────────────────────────────────────────────────┘

Nous ZÉRO FRUSTRATION sur vos chantiers, Jean.
Répondez dès aujourd'hui SVP !

Support urgence 24h/24 : 05-XX-XX-XX
support@gedimat.fr

Cordialement,
[Nom Account Manager]
Gedimat

═════════════════════════════════════════════════════════════

ÉTAPE 3 : APPEL TÉLÉPHONIQUE (Mercredi 10h, si client VIP ou pas réponse SMS)

Script appel 3 min :

"Bonjour Jean, c'est [Nom] de Gedimat.
J'appelle rapide car votre commande #1234 a un petit retard jeudi.

J'ai 3 bonnes nouvelles pour vous :
1️⃣ RETRAIT MERCREDI 17h au Dépôt (accès direct, zéro attente)
2️⃣ LIVRAISON EXPRESS JEUDI MATIN (on paie les 50€ pour toi)
3️⃣ Produit similaire IN STOCK demain (-50€ sur commande)

Qu'est-ce qui te convient best pour ton chantier lundi ?
[Écouter réponse, confirmer, noter dans CRM]

Merci Jean, c'est notre priorité !"

═════════════════════════════════════════════════════════════

ÉTAPE 4 : SUIVI RÉPONSE CLIENTE (Dashboard Ops)

Status de réponse :
☐ SMS lu (timestamp) → ✅ Pas besoin escalade
☐ Email ouvert → Email click cta ?
☐ Appel accepté solution → CRM update automatique
☐ NO RESPONSE après 24h → ESCALADE à directeur commercial

═════════════════════════════════════════════════════════════
```

---

### WORKFLOW 2 : Retard Faible + Email Standard (Urgence 6-8)

**DÉCLENCHEUR :** Retard >12h sur commande urgence 6-8
**TIMING :** J-1 avant date promise
**CANAL :** Email automatisé

```
De : noreply@gedimat.fr
Objet : Info Livraison #${ORDER_REF} - Gedimat

Bonjour ${FIRST_NAME},

Petite update sur votre commande #${ORDER_REF} →
Livraison décalée JEUDI (au lieu de MERCREDI).

Nous vous proposons :
  ✅ Réduction 5% si vous acceptez délai (+3€ crédit compte)
  ✅ Options livraison flexible (lundi matin aussi possible)

Confirmer → [LIEN]

Désolé pour ce petit retard,
Équipe Gedimat
```

---

### WORKFLOW 3 : Stock Flexible + SMS Info (Urgence 3-5)

**DÉCLENCHEUR :** Retard détecté (stock flexible, pas impactant)
**TIMING :** J-1 ou même jour
**CANAL :** SMS informatif simple

```
SMS à envoyer :

"📦 Gedimat - Cmd #4567
Livraison décalée lundi au lieu samedi.
Coû zéro pour toi.
Questions ? 05-XX-XX-XX"
```

---

## PARTIE C : TEMPLATES SEGMENTATION CRM

### Segment Profile & Actions Automatiques

```sql
-- Exemple implémentation CRM (SQL-like)

CREATE TABLE customer_urgency_profiles (
  customer_id INT PRIMARY KEY,
  segment VARCHAR(50),  -- "Artisan_Routinier", "Commanditaire", "Gros_Compte"
  avg_monthly_volume DECIMAL,
  urgency_baseline INT,  -- 3-5, 6-8, 9-10
  communication_preference VARCHAR(50),  -- SMS, Email, Appel
  ltv_status VARCHAR(50),  -- High, Medium, Low
  crm_escalation_level INT  -- 1 (Auto) to 3 (Commercial Director)
);

-- INSERT EXAMPLES :

-- Artisan Routinier - Volume faible, urgence variable
INSERT INTO customer_urgency_profiles VALUES
(1001, 'Artisan_Routinier', 1200, 6, 'SMS+Email', 'Medium', 1);

-- Commanditaire - Volume moyen, urgence élevée
INSERT INTO customer_urgency_profiles VALUES
(2001, 'Commanditaire', 4500, 8, 'Email+Call', 'High', 2);

-- Gros Compte - Volume très élevé, urgence max
INSERT INTO customer_urgency_profiles VALUES
(3001, 'Gros_Compte', 15000, 10, 'Call+Email', 'Critical', 3);

-- RÈGLES AUTOMATISMES :

IF cmd.urgency_score >= 9 AND cmd.status = "Delayed_24h+"
  THEN {
    send_sms_alert(customer_id, cmd_ref);
    send_email_options(customer_id, cmd_ref);
    IF customer.crm_escalation_level >= 2
      THEN create_call_reminder(account_manager, customer_id, "URGENT");
  }

IF cmd.urgency_score BETWEEN 6 AND 8 AND cmd.status = "Delayed_12h+"
  THEN send_email_info(customer_id, cmd_ref);

IF cmd.urgency_score <= 5
  THEN send_sms_info_only(customer_id, cmd_ref);
```

---

## PARTIE D : DASHBOARD OPÉRATIONNEL - Template JSON

```json
{
  "dashboard_name": "Gedimat - Retards & Satisfaction Real-Time",
  "timestamp": "2025-01-15T10:30:00Z",
  "kpis_summary": {
    "commandes_en_retard_urgence_9_10": 3,
    "commandes_en_retard_urgence_6_8": 7,
    "commandes_en_retard_urgence_3_5": 15,
    "sms_envoyés_ce_jour": 18,
    "taux_réponse_sms_24h": 0.72,
    "appels_clients_placés": 5,
    "solutions_acceptées": 4,
    "escalades_commerciales": 1
  },
  "commandes_urgentes_en_retard": [
    {
      "order_id": "#1234",
      "customer_name": "Jean ROUSSEAU",
      "urgency_score": 10,
      "delayed_hours": 28,
      "communication_sent": ["SMS 09:15", "Email 09:45"],
      "status": "Awaiting Response",
      "options_offered": ["Retrait Mercredi", "Express +50€", "Produit Alternatif"],
      "responsible_account_manager": "Marie Martin",
      "escalation_flag": false
    },
    {
      "order_id": "#5678",
      "customer_name": "Marc LEBLANC",
      "urgency_score": 9,
      "delayed_hours": 12,
      "communication_sent": ["Call 10:30 - Accepted Option 2"],
      "status": "Solution Agreed",
      "solution": "Livraison Express Jeudi",
      "customer_satisfaction": "Satisfied",
      "responsible_account_manager": "Marc Dupont",
      "escalation_flag": false
    }
  ],
  "sondages_satisfaction_pending": [
    {
      "order_id": "#9012",
      "customer_name": "Sophie MARTIN",
      "days_since_delivery": 1,
      "sondage_sent": "2025-01-14T16:30:00Z",
      "status": "Awaiting Response",
      "follow_up_sms_scheduled": "2025-01-21T09:00:00Z"
    }
  ],
  "insights_verbatims_top_3": [
    {
      "theme": "Délai commande",
      "mentions": 38,
      "exemple": "Too long to place and confirm order"
    },
    {
      "theme": "Accès catalogue",
      "mentions": 28,
      "exemple": "Website navigation is confusing"
    },
    {
      "theme": "Service SAV",
      "mentions": 18,
      "exemple": "Can't reach support team quickly"
    }
  ]
}
```

---

## PARTIE E : Checklist Implémentation (Roadmap)

### Semaine 1 : Setup & Test

- [ ] Finaliser template sondage CSAT (5 questions)
- [ ] Intégrer email automation (48h post-livraison)
- [ ] Tester envoi SMS relance (échantillon 50 clients)
- [ ] Mettre en place scoring urgence dans CRM (ou spreadsheet)
- [ ] Former équipe commercial sur script appel retard

### Semaine 2 : Workflow Retard

- [ ] Intégrer détection retard automatique (ERP/Tracking)
- [ ] Setup SMS alerte workflow (urgence 9-10)
- [ ] Template email options livraison (3 alternatives)
- [ ] Dashboard ops temps réel (minimal viable)

### Semaine 3-4 : Interviews & Analyse

- [ ] Planifier 8 interviews qualitatives (2 par segment)
- [ ] Analyser friction points verbatims
- [ ] Préparer rapports NPS/CSAT mensuels
- [ ] Calibrer cibles réalistes par trimestre

### Mois 2 : Optimisation

- [ ] Ajuster taux réponse sondage (ajouter relances)
- [ ] Itérer templates email basé sur feedback
- [ ] Tracker ROI communication proactive
- [ ] Préparer comité direction avec premiers KPIs

---

## PARTIE F : Configuration Email Automation (Mailchimp/SendGrid/Klaviyo)

### Trigger : "Order Delivered"

```
Automation Name: "CSAT Post-Livraison 48h"

Trigger:
  Event: "Order Status = Delivered"
  Wait: 48 hours

Send Email:
  Template: "CSAT_Post_Livraison_5Q"
  From: noreply@gedimat.fr
  Subject: "⭐ Merci ! Votre avis en 2 minutes"

Conditional Branch:
  IF: No click within 7 days
    THEN: Send SMS follow-up (optional)
    AND: Wait 3 more days

  IF: Click received
    THEN: Stop automation (survey viewed)

Post-Action:
  Capture responses in database
  Auto-calculate CSAT score
  Trigger follow-up workflow if score <= 3
```

---

**Document Technique | Gedimat 2025**
**Responsable Implementation :** IT / Marketing Operations
**Version :** 1.0 | Production Ready
