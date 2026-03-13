# EU Digital Omnibus – Consultation Feedback Analysis

## Clusters

Filtering: excludes cluster -1 (noise), cluster 0, and individual rows labeled OUTLIER.
Similarity = average TF-IDF cosine similarity between each cluster's centroid and all other cluster centroids.

N matched = count of rows with `matched? = yes`; avg costs = mean of `org_costs` midpoints (€) for matched rows; N meetings = sum of `org_meetings` for matched rows.

| Cluster | Name | Docs | Similarity | N matched | Avg costs (€) | N meetings |
|---------|------|-----:|----------:|----------:|--------------:|-----------:|
| 10 | Compliance concerns | 42 | 0.6440 | 39 | 1,424,358 | 2820 |
| 18 | Cyber concerns | 27 | 0.5878 | 20 | 178,374 | 95 |
| 6 | Ad businesses | 24 | 0.4620 | 20 | 440,789 | 387 |
| 3 | *(unnamed)* | 20 | 0.3707 | 7 | 147,142 | 26 |
| 9 | Risk & consent, simplification, compliance costs | 19 | 0.6609 | 15 | 1,280,000 | 707 |
| 2 | Compliance costs, legal certainty, metadata use | 16 | 0.3839 | 7 | 111,250 | 6 |
| 7 | Consent and rights advocacy | 16 | 0.4483 | 3 | 3,509,667 | 286 |
| 13 | Ethics, risk and human rights | 15 | 0.5051 | 13 | 3,624,611 | 413 |
| 11 | Health and biotech, device focus | 13 | 0.4817 | 7 | 650,000 | 128 |
| 4 | Innovation, legal certainty and compliance costs | 12 | 0.6288 | 12 | 1,420,000 | 509 |
| 12 | Domestic growth/competitiveness, digital sovereignty | 12 | 0.5343 | 11 | 315,000 | 114 |
| 19 | CRA and other reporting obligations | 12 | 0.6316 | 10 | 1,422,500 | 247 |
| 5 | Digital rights advocacy | 11 | 0.6079 | 10 | 4,099,203 | 105 |
| 16 | Financial, municipal and legal services | 10 | 0.5881 | 10 | 1,580,000 | 342 |
| 21 | *(unnamed)* | 10 | 0.6329 | 5 | 909,632 | 94 |
| 1 | *(unnamed)* | 9 | 0.1386 | 5 | 385,000 | 34 |
| 17 | Financial, municipal and legal services | 8 | 0.5295 | 4 | 491,250 | 87 |
| 15 | Financial industry, CRA and other reporting obligations | 7 | 0.3531 | 6 | 541,666 | 56 |
| 20 | *(unnamed)* | 6 | 0.5674 | 3 | 358,333 | 29 |
| 8 | *(unnamed)* | 5 | 0.5511 | 5 | 930,486 | 228 |
| 14 | *(unnamed)* | 5 | 0.5911 | 5 | 504,374 | 69 |

---

## Top Organisations by Meetings

Matched respondents only. Meetings = declared number of meetings with EU institutions in the Transparency Register. Deduplicated by organisation (max value taken where an org appears in multiple clusters).

| Meetings | Organisation |
|---:|---|
| 435 | BUSINESSEUROPE |
| 355 | Google |
| 286 | Airbus |
| 276 | Bureau Européen des Unions de Consommateurs |
| 222 | Meta Platforms Ireland Limited and its various subsidiaries |

---

## Top Organisations by Declared Lobbying Costs

Matched respondents only; restricted to organisations declared as "Promotes their own interests or the collective interests of their members" (Cat2) to exclude think tanks and public bodies, whose cost field reflects total organisational budget rather than lobbying expenditure. Costs = midpoint of declared cost range in the Transparency Register (€).

| Declared costs (€) | Organisation |
|---:|---|
| 9,500,000 | Meta Platforms Ireland Limited and its various subsidiaries |
| 7,500,000 | Bayer AG |
| 6,250,000 | Insurance Europe |
| 6,250,000 | Google |
| 6,250,000 | BUSINESSEUROPE |

---

## Notable Organisations by Cluster

Up to 10 organisations per cluster, ranked by prominence (meetings with EU institutions × 10,000 + log-scaled lobbying costs; matched organisations ranked above unmatched). Cluster names as assigned by BERTopic; unnamed clusters reflect insufficient label coherence.

**Cluster 10: Compliance concerns (42)**

**__Notable orgs__**: BUSINESSEUROPE, European Automobile Manufacturers' Association, Bundesverband der Deutschen Industrie e.V., DIGITALEUROPE, American Chamber of Commerce to the European Union, Telefonica S.A., Volkswagen Aktiengesellschaft, Siemens AG, Orange, Bayerische Motoren Werke Aktiengesellschaft

**Cluster 18: Cyber concerns (27)**

**__Notable orgs__**: European Express Association, CLOUD INFRASTRUCTURE SERVICES PROVIDERS IN EUROPE, Palo Alto Networks Inc., Meetic Group (a Match Group Company), Kaspersky Labs Limited, Dansk Standard, Trellix, European Committee for Standardization, Confederation of European Security Services, International Information System Security Certification Consortium Inc.

**Cluster 6: Ad businesses (24)**

**__Notable orgs__**: EBU-UER (European Broadcasting Union), European Magazine Media Association, Association of Commercial Television and Video on Demand Services in Europe, European Publishers Council, Center for Countering Digital Hate Ltd., News Media Europe, Interactive Advertising Bureau Europe, World Federation of Advertisers, Bundesverband Digitalpublisher und Zeitungsverleger, MFE - MEDIAFOREUROPE N.V

**Cluster 3: UNNAMED (20)**

**__Notable orgs__**: FEDIL - The Voice of Luxembourg's Industry, Almega, Prosus, Delivery Platforms Europe, European Justice Forum, European Games Developer Federation, DOCUSIGN INC, U.S. Chamber of Commerce

**Cluster 9: Risk & consent, simplification, compliance costs (19)**

**__Notable orgs__**: Google, Amazon Europe Core SARL, Uber, Ingka Services A.B., DOT Europe, Ecommerce Europe, Inter Ikea Systems BV, Dassault Systèmes, European Tech Alliance, Computer and Communications Industry Association

**Cluster 2: Compliance costs, legal certainty, metadata use (16)**

**__Notable orgs__**: Eurosmart, European Signature Dialog - Associated European Trust Centers, InfoCert SpA, Namirial S.p.A., European Crypto Initiative, Capgemini Deutschland GmbH, D-Trust, DigitalTrade4.EU, Entrust SAS, Evotrust

**Cluster 7: Consent and rights advocacy (16)**

**__Notable orgs__**: Bureau Européen des Unions de Consommateurs, noyb - European Center for Digital Rights, European Law Institute, Agilitation, AI Accountability Lab, Trinity College Dublin, Alexander von Humboldt Institute for Internet and Society, Alliance for Responsible Data Collection, CNIL (French Data Protection Authority), eyeo GmbH

**Cluster 13: Ethics, risk and human rights (15)**

**__Notable orgs__**: Airbus, Danish Institute for Human Rights, European Disability Forum, Democracy Reporting International, Equinet - the European Network of Equality Bodies, LinkedIn Ireland, European Network of National Human Rights Institutions, Centre for Democracy & Technology Europe, Lenovo Group Limited, IDEMIA France

**Cluster 11: Health and biotech, device focus (13)**

**__Notable orgs__**: MedTech Europe, Koninklijke Philips, ENEDIS, Siemens Healthineers AG, European Coordination Committee of the Radiological Electromedical and healthcare IT Industry, European Hearing Instrument Manufacturers Association, Zimmer Biomet Holdings, BioMed Alliance, BVMed - Bundesverband Medizintechnologie e.V., DigiFinland

**Cluster 4: Innovation, legal certainty and compliance costs (12)**

**__Notable orgs__**: Meta Platforms Ireland Limited and its various subsidiaries, IBM Corporation, Bolt, SAP, Workday, Broadcom, Skyscanner Limited, TIC Council, DER MITTELSTANDSVERBUND, Open-Xchange AG

**Cluster 12: Domestic growth/competitiveness, digital sovereignty (12)**

**__Notable orgs__**: AIM - European Brands Association, Standing Committee of European Doctors, Independent Retail Europe, Shopify Inc., European Entrepreneurs CEA-PME, European Travel Retail Confederation, European DIGITAL SME Alliance, Zentralverband Deutsches Baugewerbe, FREE ICT EUROPE FOUNDATION

**Cluster 19: CRA and other reporting obligations (12)**

**__Notable orgs__**: Bayer AG, SGI Europe, Wirtschaftskammer Österreich, France Digitale, Decathlon SE, Wolt Enterprises, Irish Farmers' Association, OpenAI OpCo LLC, Data & Technology For Compliance Alliance, Charter of Trust

**Cluster 5: Digital rights advocacy (11)**

**__Notable orgs__**: Verbraucherzentrale Bundesverband, European Partnership for Democracy, European Digital Rights, Access Now Europe, Video Games Europe, epicenter.works - Plattform Grundrechtspolitik, Culture Action Europe, The International Confederation of Music Publishers, Vorwerk SE & Co. KG, People vs Big Tech

**Cluster 16: Financial, municipal and legal services (10)**

**__Notable orgs__**: Association for Financial Markets in Europe, European Banking Federation, Mastercard Europe, London Stock Exchange Group, European Association of Co-operative Banks, European Savings and Retail Banking Group, ING Group, Eurofinas, Asociación Nacional de Establecimientos Financieros de Crédito (ASNEF), Asociación de Instituciones de Inversión Colectiva y Fondos de Pensiones

**Cluster 21: UNNAMED (10)**

**__Notable orgs__**: Vereinigung der österreichischen Industrie - Industriellenvereinigung, BSA | The Software Alliance, Centre for Information Policy Leadership (CIPL) at Hunton Andrews Kurth LLP, The European Association of On-Demand Mobility, Siinda, Dawex, Dedalus S.p.A., Global Data Alliance, Plateforme de la filière Automobile

**Cluster 1: UNNAMED (9)**

**__Notable orgs__**: The Guild of European Research-Intensive Universities, Deutscher Anwaltverein (German Bar Association), ESOMAR, Bundesverband Großhandel Außenhandel Dienstleistungen e.V., EuroGeographics, AK Wien, BUGLAS e.V., Chamber of Commerce and Industry for Munich and Upper Bavaria, Doctrine

**Cluster 17: Financial, municipal and legal services (8)**

**__Notable orgs__**: EUROCHAMBRES – Association of European Chambers of Commerce and Industry, Local Government Denmark, Indeed, Österreichische Notariatskammer, Clever Cloud, Council of European Municipalities and Regions (CEMR), Digital Poland Association

**Cluster 15: Financial industry, CRA and other reporting obligations (7)**

**__Notable orgs__**: Federation of European Securities Exchanges, Association Luxembourgeoise des Fonds d'Investissement, PensionsEurope, Assuralia, All Terrain Vehicle Industry European Association, European Association of Internal Combustion Engine and Alternative Powertrain Manufacturers, IDRS Platform

**Cluster 20: UNNAMED (6)**

**__Notable orgs__**: European Tyre & Rubber Manufacturers' Association, CIO Platform Nederland, eco - Verband der Internetwirtschaft, Government Office of the Czech Republic, Luxembourg Ministère d'État

**Cluster 8: UNNAMED (5)**

**__Notable orgs__**: ENEL SpA, ENGIE, European Federation of Engineering Consultancy Associations, Elia Transmission Belgium, Federation of European Risk Management Associations

**Cluster 14: UNNAMED (5)**

**__Notable orgs__**: TikTok Technology Ltd, Salesforce Inc., Mistral AI, Bundesverband der Unternehmen der Künstlichen Intelligenz in Deutschland e.V., European AI Forum

---

## Respondent Types

Total dataset: 374 documents.

| User Type | Count | % |
|---|---:|---:|
| BUSINESS_ASSOCIATION | 156 | 41.71% |
| COMPANY | 106 | 28.34% |
| NGO | 30 | 8.02% |
| EU_CITIZEN | 23 | 6.15% |
| OTHER | 20 | 5.35% |
| ACADEMIC_RESEARCH_INSTITTUTION | 15 | 4.01% |
| PUBLIC_AUTHORITY | 11 | 2.94% |
| TRADE_UNION | 5 | 1.34% |
| CONSUMER_ORGANISATION | 5 | 1.34% |
| NON_EU_CITIZEN | 3 | 0.80% |
