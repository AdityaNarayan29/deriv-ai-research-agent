"""Hardcoded demo data for UI development without burning API credits.

Based on real, publicly available information from SEC filings, FINRA BrokerCheck,
court records, and investigative journalism about Timothy Overturf and Sisu Capital.
"""

DEMO_TARGET_NAME = "Timothy Overturf"
DEMO_TARGET_CONTEXT = "CEO of Sisu Capital"

DEMO_FACTS = [
    # --- Professional / Corporate ---
    {
        "id": "fact-001",
        "subject": "Timothy Overturf",
        "predicate": "founded and serves as CEO of",
        "object": "Sisu Capital",
        "source_url": "https://adviserinfo.sec.gov/firm/summary/169444",
        "confidence": 0.97,
        "category": "professional",
    },
    {
        "id": "fact-002",
        "subject": "Sisu Capital",
        "predicate": "is registered investment adviser (CRD# 169444) regulated by",
        "object": "FINRA",
        "source_url": "https://adviserinfo.sec.gov/firm/summary/169444",
        "confidence": 0.98,
        "category": "regulatory",
    },
    {
        "id": "fact-003",
        "subject": "Timothy Overturf",
        "predicate": "is registered representative (CRD# 6422933) supervised by",
        "object": "FINRA",
        "source_url": "https://reports.adviserinfo.sec.gov/reports/individual/individual_6422933.pdf",
        "confidence": 0.98,
        "category": "regulatory",
    },
    {
        "id": "fact-004",
        "subject": "Sisu Capital",
        "predicate": "was incorporated on Oct 25, 2013 in",
        "object": "Mill Valley, California",
        "source_url": "https://www.corporationwiki.com/p/2l6ore/timothy-silas-prugh-overturf",
        "confidence": 0.90,
        "category": "professional",
    },
    {
        "id": "fact-005",
        "subject": "Timothy Overturf",
        "predicate": "managed ~$51.7M in client assets through",
        "object": "Sisu Capital",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.92,
        "category": "financial",
    },
    {
        "id": "fact-006",
        "subject": "Sisu Capital",
        "predicate": "operated from registered office in",
        "object": "Arcata, California",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.88,
        "category": "professional",
    },
    {
        "id": "fact-007",
        "subject": "Overturf Financial Services",
        "predicate": "was predecessor firm of",
        "object": "Sisu Capital",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.85,
        "category": "professional",
    },
    {
        "id": "fact-008",
        "subject": "Sisu Capital",
        "predicate": "was headquartered in",
        "object": "Mill Valley, California",
        "source_url": "https://adviserinfo.sec.gov/firm/summary/169444",
        "confidence": 0.95,
        "category": "professional",
    },
    {
        "id": "fact-009",
        "subject": "Timothy Overturf",
        "predicate": "operated Sisu Capital from",
        "object": "Arcata, California",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.85,
        "category": "biographical",
    },
    # --- Family / Hans Overturf ---
    {
        "id": "fact-010",
        "subject": "Hansueli Overturf",
        "predicate": "is the father of",
        "object": "Timothy Overturf",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.95,
        "category": "biographical",
    },
    {
        "id": "fact-011",
        "subject": "Hansueli Overturf",
        "predicate": "is co-defendant alongside Timothy Overturf in",
        "object": "SEC v. Sisu Capital (3:23-cv-03855)",
        "source_url": "https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25807",
        "confidence": 0.97,
        "category": "legal",
    },
    {
        "id": "fact-012",
        "subject": "Hansueli Overturf",
        "predicate": "provided unauthorized investment advice to clients of",
        "object": "Sisu Capital",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.93,
        "category": "legal",
    },
    {
        "id": "fact-013",
        "subject": "Hansueli Overturf",
        "predicate": "is registered representative (CRD# 4138916) regulated by",
        "object": "FINRA",
        "source_url": "https://brokercheck.finra.org/Individual/4138916",
        "confidence": 0.98,
        "category": "regulatory",
    },
    {
        "id": "fact-014",
        "subject": "Hansueli Overturf",
        "predicate": "was previously employed at",
        "object": "Morgan Stanley",
        "source_url": "https://hans-overturf.blogspot.com/p/about-hans-overturf.html",
        "confidence": 0.85,
        "category": "professional",
    },
    {
        "id": "fact-015",
        "subject": "Hansueli Overturf",
        "predicate": "operated through",
        "object": "Raymond James Financial Services",
        "source_url": "https://brokercheck.finra.org/Individual/4138916",
        "confidence": 0.88,
        "category": "professional",
    },
    {
        "id": "fact-016",
        "subject": "Hansueli Overturf",
        "predicate": "founded",
        "object": "Overturf Financial Services",
        "source_url": "https://dfpi.ca.gov/enforcement_action/overturf-financial-services-inc/",
        "confidence": 0.90,
        "category": "professional",
    },
    {
        "id": "fact-017",
        "subject": "FINRA",
        "predicate": "fined $10,000 and suspended in 2011",
        "object": "Hansueli Overturf",
        "source_url": "https://brokercheck.finra.org/Individual/4138916",
        "confidence": 0.95,
        "category": "regulatory",
    },
    {
        "id": "fact-018",
        "subject": "Hansueli Overturf",
        "predicate": "graduated from",
        "object": "Humboldt State University",
        "source_url": "https://hans-overturf.blogspot.com/p/about-hans-overturf.html",
        "confidence": 0.80,
        "category": "biographical",
    },
    {
        "id": "fact-019",
        "subject": "Hansueli Overturf",
        "predicate": "formerly operated from offices in",
        "object": "Eureka, California",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.82,
        "category": "biographical",
    },
    # --- SEC Enforcement ---
    {
        "id": "fact-020",
        "subject": "SEC",
        "predicate": "filed civil complaint (LR-25807) on Aug 1, 2023 against",
        "object": "Sisu Capital",
        "source_url": "https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25807",
        "confidence": 0.98,
        "category": "legal",
    },
    {
        "id": "fact-021",
        "subject": "SEC",
        "predicate": "charged violations of Sections 206(1) and 206(2) Investment Advisers Act against",
        "object": "Timothy Overturf",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.97,
        "category": "legal",
    },
    {
        "id": "fact-022",
        "subject": "SEC",
        "predicate": "charged Hansueli Overturf with aiding and abetting violations by",
        "object": "Sisu Capital",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.95,
        "category": "legal",
    },
    {
        "id": "fact-023",
        "subject": "Timothy Overturf",
        "predicate": "drew approximately $858,000 in owner draws/loans from",
        "object": "Sisu Capital",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.90,
        "category": "financial",
    },
    {
        "id": "fact-024",
        "subject": "SEC",
        "predicate": "alleges $2M+ in excessive advisory fees collected by",
        "object": "Sisu Capital",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.92,
        "category": "financial",
    },
    {
        "id": "fact-025",
        "subject": "Sisu Capital",
        "predicate": "invested clients in unsuitable inverse volatility products via",
        "object": "Redwood Capital Bancorp",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.91,
        "category": "financial",
    },
    # --- Redwood Capital Bancorp ---
    {
        "id": "fact-026",
        "subject": "Timothy Overturf",
        "predicate": "made unauthorized purchases of thinly-traded stock in",
        "object": "Redwood Capital Bancorp",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.93,
        "category": "financial",
    },
    {
        "id": "fact-027",
        "subject": "Redwood Capital Bancorp",
        "predicate": "is headquartered near Sisu Capital operations in",
        "object": "Eureka, California",
        "source_url": "https://www.redwoodcapitalbank.com/",
        "confidence": 0.88,
        "category": "financial",
    },
    {
        "id": "fact-028",
        "subject": "SEC",
        "predicate": "charged unauthorized purchase of 2,300+ RWCB shares by",
        "object": "Timothy Overturf",
        "source_url": "https://www.sec.gov/files/litigation/complaints/2023/comp25807.pdf",
        "confidence": 0.91,
        "category": "financial",
    },
    # --- California DFPI ---
    {
        "id": "fact-029",
        "subject": "California DFPI",
        "predicate": "summarily revoked investment adviser certificate of",
        "object": "Sisu Capital",
        "source_url": "https://dfpi.ca.gov/enf-s/sisu-capital-llc/",
        "confidence": 0.96,
        "category": "regulatory",
    },
    {
        "id": "fact-030",
        "subject": "California DFPI",
        "predicate": "issued desist and refrain orders against",
        "object": "Overturf Financial Services",
        "source_url": "https://dfpi.ca.gov/enforcement_action/overturf-financial-services-inc/",
        "confidence": 0.92,
        "category": "regulatory",
    },
    # --- Court Case ---
    {
        "id": "fact-031",
        "subject": "SEC v. Sisu Capital",
        "predicate": "is assigned case number 3:23-cv-03855 in",
        "object": "U.S. District Court, Northern District of California",
        "source_url": "https://dockets.justia.com/docket/california/candce/3:2023cv03855/416262",
        "confidence": 0.98,
        "category": "legal",
    },
    {
        "id": "fact-032",
        "subject": "Judge Jacqueline Scott Corley",
        "predicate": "presides over",
        "object": "SEC v. Sisu Capital (3:23-cv-03855)",
        "source_url": "https://dockets.justia.com/docket/california/candce/3:2023cv03855/416262",
        "confidence": 0.95,
        "category": "legal",
    },
    {
        "id": "fact-033",
        "subject": "Hansueli Overturf",
        "predicate": "represents himself pro se in",
        "object": "SEC v. Sisu Capital (3:23-cv-03855)",
        "source_url": "https://www.courtlistener.com/docket/67656798/securities-and-exchange-commission-v-sisu-capital-llc/",
        "confidence": 0.88,
        "category": "legal",
    },
    # --- Arcata Theatre Lounge / Joseppi's ---
    {
        "id": "fact-034",
        "subject": "Timothy Overturf",
        "predicate": "co-purchased in 2019 with Joseph Ostini",
        "object": "Arcata Theatre Lounge",
        "source_url": "https://lostcoastoutpost.com/2019/jul/12/ambitious-twentysomethings-buy-arcata-theatre-loun/",
        "confidence": 0.92,
        "category": "professional",
    },
    {
        "id": "fact-035",
        "subject": "Joseppi's LLC",
        "predicate": "operates as DBA for",
        "object": "Arcata Theatre Lounge",
        "source_url": "https://lostcoastoutpost.com/2019/jul/12/ambitious-twentysomethings-buy-arcata-theatre-loun/",
        "confidence": 0.90,
        "category": "professional",
    },
    {
        "id": "fact-036",
        "subject": "NLRB",
        "predicate": "found unfair labor practices (Case 20-CA-292430) against",
        "object": "Joseppi's LLC",
        "source_url": "https://www.nlrb.gov/case/20-CA-292430",
        "confidence": 0.95,
        "category": "legal",
    },
    {
        "id": "fact-037",
        "subject": "Ninth Circuit Court of Appeals",
        "predicate": "enforced NLRB order against",
        "object": "Joseppi's LLC",
        "source_url": "https://lostcoastoutpost.com/2023/jul/25/labor-relations-board-orders-arcata-theatre-lounge/",
        "confidence": 0.90,
        "category": "legal",
    },
    # --- Other entities ---
    {
        "id": "fact-038",
        "subject": "Timothy Overturf",
        "predicate": "is listed as President of",
        "object": "Noir Execution Inc",
        "source_url": "https://www.corporationwiki.com/p/393zm0/timothy-silas-prugh-overturf",
        "confidence": 0.82,
        "category": "professional",
    },
    {
        "id": "fact-039",
        "subject": "Timothy Overturf",
        "predicate": "passed Series 65 exam and registered as adviser representative with",
        "object": "California DFPI",
        "source_url": "https://reports.adviserinfo.sec.gov/reports/individual/individual_6422933.pdf",
        "confidence": 0.95,
        "category": "regulatory",
    },
    {
        "id": "fact-040",
        "subject": "Timothy Overturf",
        "predicate": "was approximately 18 years old when he founded",
        "object": "Sisu Capital",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.85,
        "category": "biographical",
    },
    {
        "id": "fact-041",
        "subject": "Hansueli Overturf",
        "predicate": "was accused in 2004 of bilking $730,000 from elderly patients via",
        "object": "Redwood Parks Lodge",
        "source_url": "https://lostcoastoutpost.com/2023/aug/18/sec-accuses-timothy-overturf-owner-and-ceo-local-i/",
        "confidence": 0.87,
        "category": "legal",
    },
    {
        "id": "fact-042",
        "subject": "Alice Liu Jensen",
        "predicate": "led SEC investigation of",
        "object": "Sisu Capital",
        "source_url": "https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25807",
        "confidence": 0.90,
        "category": "legal",
    },
    {
        "id": "fact-043",
        "subject": "KlaymanToskes",
        "predicate": "announced misconduct investigation into",
        "object": "Timothy Overturf",
        "source_url": "https://klaymantoskes.com/broker-investigation/advisor-timothy-overturf/",
        "confidence": 0.88,
        "category": "legal",
    },
    {
        "id": "fact-044",
        "subject": "Joseph Ostini",
        "predicate": "is business partner of Timothy Overturf and co-owner of",
        "object": "Joseppi's LLC",
        "source_url": "https://lostcoastoutpost.com/2019/jul/12/ambitious-twentysomethings-buy-arcata-theatre-loun/",
        "confidence": 0.90,
        "category": "professional",
    },
    {
        "id": "fact-045",
        "subject": "Redwood Capital Bancorp",
        "predicate": "is a community bank headquartered in",
        "object": "Eureka, California",
        "source_url": "https://www.redwoodcapitalbank.com/",
        "confidence": 0.90,
        "category": "professional",
    },
]

DEMO_ENTITIES = [
    {
        "id": "ent-001",
        "name": "Timothy Overturf",
        "entity_type": "person",
        "description": "CEO and founder of Sisu Capital; CRD# 6422933; founded firm at age 18",
        "investigated": True,
    },
    {
        "id": "ent-002",
        "name": "Sisu Capital",
        "entity_type": "organization",
        "description": "Investment advisory firm (CRD# 169444); managed ~$51.7M for 42 clients; certificate revoked by CA DFPI",
        "investigated": True,
    },
    {
        "id": "ent-003",
        "name": "Hansueli Overturf",
        "entity_type": "person",
        "description": "Father of Timothy; co-defendant in SEC case; CRD# 4138916; FINRA-suspended; resides in Switzerland",
        "investigated": True,
    },
    {
        "id": "ent-004",
        "name": "SEC",
        "entity_type": "organization",
        "description": "U.S. Securities and Exchange Commission; filed civil fraud complaint LR-25807 on Aug 1, 2023",
        "investigated": True,
    },
    {
        "id": "ent-005",
        "name": "FINRA",
        "entity_type": "organization",
        "description": "Financial Industry Regulatory Authority; fined and suspended Hansueli Overturf in 2011",
        "investigated": True,
    },
    {
        "id": "ent-006",
        "name": "California DFPI",
        "entity_type": "organization",
        "description": "CA Dept of Financial Protection & Innovation; revoked Sisu Capital certificate; multiple actions against Overturf Financial Services",
        "investigated": True,
    },
    {
        "id": "ent-007",
        "name": "Overturf Financial Services",
        "entity_type": "organization",
        "description": "Hans Overturf's prior investment advisory firm; offices in Mill Valley, Arcata, SF; subject to DFPI enforcement",
        "investigated": True,
    },
    {
        "id": "ent-008",
        "name": "Joseppi's LLC",
        "entity_type": "organization",
        "description": "Business entity formed by Overturf and Ostini to acquire Arcata Theatre Lounge; found guilty of NLRB violations",
        "investigated": True,
    },
    {
        "id": "ent-009",
        "name": "Arcata Theatre Lounge",
        "entity_type": "organization",
        "description": "Historic Art Deco entertainment venue in Arcata, CA; DBA of Joseppi's LLC; purchased 2019",
        "investigated": False,
    },
    {
        "id": "ent-010",
        "name": "Joseph Ostini",
        "entity_type": "person",
        "description": "Business partner of Timothy Overturf; co-purchased Arcata Theatre Lounge via Joseppi's LLC in 2019",
        "investigated": False,
    },
    {
        "id": "ent-011",
        "name": "Redwood Capital Bancorp",
        "entity_type": "organization",
        "description": "Community bank holding company (OTCQB: RWCB) in Eureka, CA; stock used in unauthorized trading scheme",
        "investigated": True,
    },
    {
        "id": "ent-012",
        "name": "Noir Execution Inc",
        "entity_type": "organization",
        "description": "California corporation incorporated ~Sept 2020; Timothy Overturf listed as President",
        "investigated": False,
    },
    {
        "id": "ent-013",
        "name": "Morgan Stanley",
        "entity_type": "organization",
        "description": "Major financial services firm where Hans Overturf was previously employed in Eureka, CA",
        "investigated": False,
    },
    {
        "id": "ent-014",
        "name": "Raymond James Financial Services",
        "entity_type": "organization",
        "description": "Financial services firm; Hans Overturf operated through their Arcata, CA branch (2003-2008)",
        "investigated": False,
    },
    {
        "id": "ent-015",
        "name": "NLRB",
        "entity_type": "organization",
        "description": "National Labor Relations Board; found unfair labor practices by Joseppi's LLC (Case 20-CA-292430)",
        "investigated": True,
    },
    {
        "id": "ent-016",
        "name": "Ninth Circuit Court of Appeals",
        "entity_type": "organization",
        "description": "Federal appeals court; enforced NLRB order against Joseppi's LLC in July 2023",
        "investigated": False,
    },
    {
        "id": "ent-017",
        "name": "U.S. District Court, Northern District of California",
        "entity_type": "organization",
        "description": "Federal court in San Francisco; venue for SEC v. Sisu Capital (Case 3:23-cv-03855)",
        "investigated": False,
    },
    {
        "id": "ent-018",
        "name": "Judge Jacqueline Scott Corley",
        "entity_type": "person",
        "description": "U.S. District Judge presiding over SEC v. Sisu Capital in NDCA",
        "investigated": False,
    },
    {
        "id": "ent-019",
        "name": "Alice Liu Jensen",
        "entity_type": "person",
        "description": "SEC staff attorney who led the investigation and serves as trial counsel",
        "investigated": False,
    },
    {
        "id": "ent-020",
        "name": "KlaymanToskes",
        "entity_type": "organization",
        "description": "Securities law firm that announced a separate misconduct investigation into Timothy Overturf",
        "investigated": False,
    },
    {
        "id": "ent-021",
        "name": "Redwood Parks Lodge",
        "entity_type": "organization",
        "description": "Fraudulent investment vehicle used by Hans Overturf to defraud elderly couple of $730,000 in 2004",
        "investigated": False,
    },
    {
        "id": "ent-022",
        "name": "Humboldt State University",
        "entity_type": "organization",
        "description": "University where Hans Overturf graduated Summa Cum Laude in Economics (1999); now Cal Poly Humboldt",
        "investigated": False,
    },
    {
        "id": "ent-023",
        "name": "Mill Valley, California",
        "entity_type": "location",
        "description": "Sisu Capital registered office; Overturf Financial Services headquarters at 20 Sunnyside Ave",
        "investigated": False,
    },
    {
        "id": "ent-024",
        "name": "Arcata, California",
        "entity_type": "location",
        "description": "Timothy Overturf's operational base; location of Arcata Theatre Lounge; Humboldt County",
        "investigated": False,
    },
    {
        "id": "ent-025",
        "name": "Eureka, California",
        "entity_type": "location",
        "description": "Hans Overturf's Morgan Stanley office; Redwood Capital Bank headquarters; Humboldt County seat",
        "investigated": False,
    },
    {
        "id": "ent-026",
        "name": "SEC v. Sisu Capital (3:23-cv-03855)",
        "entity_type": "filing",
        "description": "Federal civil fraud case filed Aug 1, 2023; charges violations of Investment Advisers Act Sections 206(1) & 206(2)",
        "investigated": True,
    },
]

DEMO_RISK_FLAGS = [
    {
        "id": "risk-001",
        "description": "SEC civil fraud action (LR-25807) — Timothy and Hansueli Overturf charged with breaching fiduciary duties to ~42 high-net-worth clients managing $51.7M in assets. Violations of Investment Advisers Act Sections 206(1) and 206(2).",
        "severity": 5,
        "category": "legal",
        "evidence_fact_ids": ["fact-020", "fact-021", "fact-022", "fact-005"],
        "recommendation": "Immediate disqualification from any fiduciary role. Review all SEC litigation releases and complaint exhibits.",
    },
    {
        "id": "risk-002",
        "description": "California DFPI revoked Sisu Capital's investment adviser certificate (Jan 21, 2021) — firm barred from operating as an investment adviser in the state. Multiple prior enforcement actions against Overturf Financial Services.",
        "severity": 5,
        "category": "regulatory",
        "evidence_fact_ids": ["fact-029", "fact-030"],
        "recommendation": "Verify current registration status with all 50 states. Check for any new entity registrations under different names.",
    },
    {
        "id": "risk-003",
        "description": "Unauthorized trading in thinly-traded bank stock — purchased 2,300+ shares of Redwood Capital Bancorp (RWCB) for a client who explicitly instructed to sell, potentially to manipulate the stock or leverage the bank's charter for crypto asset acceptance.",
        "severity": 5,
        "category": "financial",
        "evidence_fact_ids": ["fact-026", "fact-027", "fact-028"],
        "recommendation": "Report to SEC Market Abuse Unit. Review all client accounts for similar unauthorized trades in illiquid securities.",
    },
    {
        "id": "risk-004",
        "description": "Father-son fraud pattern — Hans Overturf (FINRA-suspended, previously fined $10K) provided unauthorized investment advice to Sisu Capital clients. Hans has prior history of bilking elderly dementia patients of $730,000 via 'Redwood Parks Lodge' scheme in 2004.",
        "severity": 5,
        "category": "reputational",
        "evidence_fact_ids": ["fact-010", "fact-012", "fact-017", "fact-041"],
        "recommendation": "Conduct full background check on all family members involved in financial services. Cross-reference Hans Overturf's client interactions.",
    },
    {
        "id": "risk-005",
        "description": "Excessive personal draws — Timothy Overturf drew approximately $858,000 in owner draws/loans from Sisu Capital (2017-2019) while firm collected >$2M in advisory fees from clients.",
        "severity": 4,
        "category": "financial",
        "evidence_fact_ids": ["fact-023", "fact-024"],
        "recommendation": "Forensic audit of all fund flows between Sisu Capital, personal accounts, and other Overturf entities.",
    },
    {
        "id": "risk-006",
        "description": "NLRB unfair labor practices — Joseppi's LLC (Overturf's entertainment venue) found guilty of unfair labor practices. Order enforced by Ninth Circuit Court of Appeals. Demonstrates pattern of disregard for regulatory compliance across multiple businesses.",
        "severity": 3,
        "category": "legal",
        "evidence_fact_ids": ["fact-036", "fact-037", "fact-034"],
        "recommendation": "Review all business entities associated with Overturf for compliance issues. Pattern suggests systemic governance failures.",
    },
    {
        "id": "risk-007",
        "description": "Shell company network — Timothy Overturf is President of Noir Execution Inc (incorporated Sept 2020), purpose unknown. Combined with Joseppi's LLC and Sisu Capital, suggests a pattern of creating multiple entities.",
        "severity": 3,
        "category": "financial",
        "evidence_fact_ids": ["fact-038", "fact-035"],
        "recommendation": "Investigate purpose of Noir Execution Inc. Check for additional entities in California Secretary of State records.",
    },
    {
        "id": "risk-008",
        "description": "Unsuitable investment products — Sisu Capital invested clients in inverse short-term volatility futures products designed for day trading, holding them for months. Indicates fundamental incompetence or deliberate mismanagement.",
        "severity": 4,
        "category": "financial",
        "evidence_fact_ids": ["fact-025"],
        "recommendation": "Review all client portfolios for suitability. Compare risk profiles of investments against client risk tolerance documentation.",
    },
]

DEMO_REPORT = """# Due Diligence Report: Timothy Overturf
*Generated: 2026-02-26 14:30:00 | Investigation ID: demo-001 | Iterations: 3*

---

## Executive Summary

This comprehensive due diligence investigation into **Timothy Overturf**, CEO of **Sisu Capital**, reveals a **multi-generational pattern of securities fraud** that demands immediate attention. The investigation uncovered a dense network of **26 connected entities** across financial services, regulatory enforcement, real estate, and entertainment ventures.

> **CRITICAL RISK RATING**: The subject is the target of an active SEC civil fraud action, has had his firm's investment adviser certificate revoked by California DFPI, and has demonstrable ties to a father with a prior history of defrauding elderly clients.

Key findings include:
- **SEC Complaint (LR-25807)**: Filed August 1, 2023, charging violations of Investment Advisers Act Sections 206(1) and 206(2)
- **$51.7 million in AUM** managed for 42 high-net-worth clients with a "2 and 20" fee structure
- **Father-son fraud dynamic**: Hansueli "Hans" Overturf provided unauthorized advice while FINRA-suspended
- **Unauthorized trading**: 2,300+ shares of thinly-traded Redwood Capital Bancorp stock purchased against client instructions
- **Multiple regulatory failures**: Actions by SEC, FINRA, California DFPI, and NLRB across related entities

| Metric | Value |
|--------|-------|
| Facts Extracted | 45 |
| Entities Discovered | 26 |
| Risk Flags | 8 (4 Critical, 2 High, 2 Elevated) |
| Search Iterations | 3 |
| Sources Analyzed | 52 |
| Overall Confidence | 91% |

---

## Subject Profile

| Field | Detail |
|-------|--------|
| **Full Legal Name** | Timothy Silas Prugh Overturf |
| **CRD Number** | 6422933 |
| **Role** | CEO & Founder, Sisu Capital |
| **Other Roles** | President, Noir Execution Inc; Co-owner, Joseppi's LLC |
| **Location** | Arcata, California (operational); Mill Valley, CA (registered) |
| **Registrations** | Series 65 (CA investment adviser representative, Nov 2014 – Dec 2020) |
| **Family** | Father: Hansueli "Hans" Overturf (CRD# 4138916, FINRA-suspended) |
| **Founded Sisu Capital** | October 25, 2013 (age ~18) |

---

## Organizational Connections

The investigation revealed a network of **26 entities** spanning five categories:

### Financial Entities
- **Sisu Capital, LLC** (CRD# 169444) — Primary investment advisory firm. Managed ~$51.7M for 42 clients. Certificate revoked by CA DFPI Jan 2021. Subject of SEC complaint.
- **Overturf Financial Services, Inc.** — Hans Overturf's prior firm. Offices in Mill Valley, Arcata, San Francisco. Subject to multiple DFPI enforcement actions (2011-2017).
- **Redwood Capital Bancorp** (OTCQB: RWCB) — Community bank in Eureka, CA. Stock was subject of unauthorized trading by Overturf. 2,300+ shares purchased for client who instructed to sell.
- **Morgan Stanley** — Hans Overturf's former employer in Eureka. Received National Director's Award.
- **Raymond James Financial Services** — Hans Overturf operated through their Arcata branch (2003-2008).

### Business Entities
- **Joseppi's LLC** — Entity formed by Timothy and Joseph Ostini to purchase Arcata Theatre Lounge. Found guilty of NLRB violations.
- **Arcata Theatre Lounge** — Historic Art Deco venue in Arcata, purchased 2019.
- **Noir Execution Inc** — California corporation, Timothy as President (incorporated ~Sept 2020). Purpose unknown.
- **Redwood Parks Lodge** — Fraudulent investment vehicle used by Hans to defraud elderly couple ($730K) in 2004.

### Regulatory Bodies
- **SEC** — Filed civil complaint LR-25807, case 3:23-cv-03855 (NDCA).
- **FINRA** — Fined and suspended Hans Overturf ($10K fine, 2011 suspension).
- **California DFPI** — Revoked Sisu Capital certificate; multiple actions against Overturf Financial Services.
- **NLRB** — Found unfair labor practices by Joseppi's LLC (Case 20-CA-292430).

### Legal
- **U.S. District Court, NDCA** — Venue for SEC v. Sisu Capital, Judge Jacqueline Scott Corley presiding.
- **Ninth Circuit Court of Appeals** — Enforced NLRB order against Joseppi's LLC.
- **KlaymanToskes** — Securities law firm conducting parallel misconduct investigation.

---

## Risk Assessment

### Risk Flag Summary

| # | Risk | Severity | Category |
|---|------|----------|----------|
| 1 | SEC Civil Fraud Action | 5/5 Critical | Legal |
| 2 | CA DFPI Certificate Revocation | 5/5 Critical | Regulatory |
| 3 | Unauthorized Trading (RWCB) | 5/5 Critical | Financial |
| 4 | Father-Son Fraud Pattern | 5/5 Critical | Reputational |
| 5 | Excessive Personal Draws | 4/5 High | Financial |
| 6 | Unsuitable Investment Products | 4/5 High | Financial |
| 7 | NLRB Labor Violations | 3/5 Elevated | Legal |
| 8 | Shell Company Network | 3/5 Elevated | Financial |

### Critical (5/5)

1. **SEC Civil Fraud Action** — Direct enforcement by the SEC (LR-25807, Aug 2023) for violations of Investment Advisers Act antifraud provisions. Case active as of Feb 2026 with settlement conference held Jan 2025. *Evidence: 4 corroborating facts from SEC filings and court records.*

2. **CA DFPI Certificate Revocation** — The most severe state-level sanction: summary revocation of Sisu Capital's investment adviser certificate (Jan 2021). Combined with multiple prior actions against Overturf Financial Services spanning 2011-2017, demonstrates persistent regulatory non-compliance. *Evidence: DFPI enforcement records.*

3. **Unauthorized Trading** — Purchased 2,300+ shares of thinly-traded Redwood Capital Bancorp (RWCB) for a client who explicitly instructed to sell. SEC complaint suggests potential market manipulation or scheme to leverage bank charter for cryptocurrency operations. *Evidence: SEC complaint exhibits, RWCB trading records.*

4. **Father-Son Fraud Pattern** — Hans Overturf (FINRA-suspended, $10K fine) provided unauthorized investment advice to Sisu Capital clients. His prior 2004 fraud involving "Redwood Parks Lodge" ($730K from elderly dementia patients) establishes a family pattern of financial exploitation. *Evidence: FINRA BrokerCheck, SEC complaint, DFPI records, Lost Coast Outpost reporting.*

### High (4/5)

5. **Excessive Personal Draws** — $858,000 in owner draws/loans from Sisu Capital (2017-2019) while managing $51.7M in client assets. Raises questions about fund misappropriation. *Evidence: SEC complaint, financial records.*

6. **Unsuitable Investment Products** — Invested clients in inverse short-term volatility futures designed for day trading, held for months. Demonstrates either fundamental incompetence or deliberate mismanagement to generate fees. *Evidence: SEC complaint.*

### Elevated (3/5)

7. **NLRB Labor Violations** — Joseppi's LLC found guilty of unfair labor practices, order enforced by Ninth Circuit. While not directly securities-related, demonstrates cross-domain regulatory non-compliance. *Evidence: NLRB Case 20-CA-292430.*

8. **Shell Company Network** — At least four entities (Sisu Capital, Joseppi's LLC, Noir Execution Inc, informal ties to Overturf Financial Services) suggest a pattern of entity creation that may obscure asset flows. *Evidence: California corporate records.*

---

## Key Findings

1. **Multi-Generational Fraud Pattern** — The father-son dynamic is the most significant non-obvious finding. Hans Overturf's 2004 fraud involving elderly dementia patients, followed by his FINRA suspension and subsequent unauthorized involvement in his son's firm, suggests that Timothy Overturf was following an established family playbook.

2. **Cross-Domain Regulatory Failures** — Enforcement actions span SEC (federal securities), FINRA (industry self-regulation), CA DFPI (state), and NLRB (labor). Four independent regulatory bodies finding violations across related entities is extraordinarily rare and indicates systemic disregard for compliance.

3. **Potential Market Manipulation** — The unauthorized accumulation of thinly-traded RWCB stock warrants further investigation. The SEC complaint hints at a larger scheme involving the bank's charter and cryptocurrency operations.

4. **Entity Proliferation** — The creation of multiple entities (Noir Execution Inc incorporated just months before Sisu Capital shuttered) may indicate asset shielding or preparation for new ventures under clean entities.

5. **Age Anomaly** — Timothy Overturf founded Sisu Capital at approximately age 18, with his FINRA-suspended father actively involved behind the scenes. This raises questions about who was truly directing the firm.

---

## Investigation Timeline

| Date | Event | Source |
|------|-------|--------|
| 2004 | Hans defrauds elderly couple of $730K via "Redwood Parks Lodge" | LCO reporting |
| 2008 | Hans leaves Raymond James, founds Overturf Financial Services | DFPI records |
| Aug 2011 | CA DFPI issues Accusation & Desist Order against Hans | DFPI |
| Nov 2011 | FINRA suspends Hans, fines $10K | FINRA BrokerCheck |
| Oct 2013 | Timothy (age ~18) incorporates Sisu Capital in California | Corp records |
| Nov 2014 | Timothy registers as CA investment adviser representative | SEC IAPD |
| 2015 | Timothy begins career, passes Series 65 exam | FINRA |
| Dec 2017 | Beginning of SEC-alleged fraud period | SEC complaint |
| 2018 | Broker-dealer terminates Sisu Capital relationship | SEC complaint |
| Jun-Aug 2019 | Timothy & Ostini purchase Arcata Theatre Lounge | LCO reporting |
| Mar 2020-2021 | Unauthorized RWCB stock purchases | SEC complaint |
| Sept 2020 | Noir Execution Inc incorporated | CA Corp records |
| Jan 2021 | CA DFPI revokes Sisu Capital certificate | DFPI |
| Dec 2020 | Timothy's adviser registration terminated | SEC IAPD |
| May 2021 | End of SEC-alleged fraud period | SEC complaint |
| Mar 2022 | NLRB complaint filed against Joseppi's LLC | NLRB |
| Apr 2023 | NLRB Board adopts ALJ decision | NLRB |
| Jul 2023 | Ninth Circuit enforces NLRB order | LCO reporting |
| Aug 1, 2023 | SEC files civil complaint (LR-25807) | SEC |
| Oct 2023 | KlaymanToskes announces misconduct investigation | KlaymanToskes |
| Jan 2025 | Settlement conference before Magistrate Judge Cisneros | Court docket |
| Feb 2026 | Case still active, no public resolution | Court docket |

---

## Confidence Assessment

- **Overall Confidence**: VERY HIGH (91%)
- **Fact Verification Rate**: 45/45 facts sourced from public records
- **Source Diversity**: SEC filings, FINRA BrokerCheck, CA DFPI records, NLRB records, court dockets (Justia, CourtListener), corporate registrations, investigative journalism (Lost Coast Outpost), law firm publications
- **Coverage Gaps**: Limited information on: current activities (post-2021), criminal proceedings (only civil identified), personal asset holdings, Noir Execution Inc's purpose

### Source Breakdown

| Source Type | Count | Reliability |
|-------------|-------|-------------|
| SEC Official Filings & Litigation | 12 | Very High |
| FINRA BrokerCheck | 4 | Very High |
| California DFPI Records | 5 | Very High |
| Court Dockets (PACER/Justia) | 6 | Very High |
| Corporate Registrations | 4 | High |
| NLRB Records | 3 | Very High |
| Investigative Journalism (LCO) | 8 | High |
| Law Firm Publications | 3 | Medium-High |
| Professional Profiles | 2 | Medium |
| Other (blogs, directories) | 5 | Medium |

---

## Recommendations

1. **Do not engage** in any fiduciary, investment, or advisory relationship with Timothy Overturf or any entity in which he is an officer, director, or beneficial owner.
2. **Monitor case resolution** — SEC v. Sisu Capital (3:23-cv-03855) is active as of Feb 2026. Settlement conference in Jan 2025 may indicate pending resolution. Track through PACER.
3. **Screen all related entities** — Run OFAC, SAM, and state-level screens on: Noir Execution Inc, Joseppi's LLC, Overturf Financial Services, and any new entity registrations.
4. **Criminal referral check** — Determine if DOJ has filed or is considering criminal charges in addition to SEC civil action.
5. **Asset tracing** — Given the multiple entity structure and Hans Overturf's relocation to Switzerland, conduct international asset search.
6. **Enhanced monitoring** — Add Timothy Overturf, Hansueli Overturf, and all related entities to ongoing adverse media monitoring.
7. **Counterparty notification** — If your organization or clients had exposure to Sisu Capital, initiate forensic review and consider regulatory notification obligations.

---

*This report was generated by the AI Research Agent. All facts are sourced from publicly available records (SEC, FINRA, DFPI, NLRB, court filings, corporate registrations). Independent verification is recommended before making business decisions.*
"""

DEMO_EXECUTION_LOG = [
    "[query_planner] Planning search queries for: Timothy Overturf (CEO of Sisu Capital)",
    "[query_planner] Generated 5 queries covering: professional, legal, regulatory, financial, biographical",
    "[search_executor] Executing 5 queries via Tavily (3 parallel workers)...",
    "[search_executor] ✓ 'Timothy Overturf CEO Sisu Capital investment adviser' — 8 results",
    "[search_executor] ✓ 'Timothy Overturf SEC enforcement action complaint' — 7 results",
    "[search_executor] ✓ 'Sisu Capital LLC CRD 169444 IAPD registration' — 5 results",
    "[search_executor] ✓ 'Timothy Overturf FINRA BrokerCheck CRD' — 4 results",
    "[search_executor] ✓ 'Timothy Overturf Arcata California background' — 6 results",
    "[search_executor] Search complete: 30 results from 5 queries in 3.1s",
    "[fact_extractor] Extracting facts from 30 search results using Groq (llama-3.3-70b)...",
    "[fact_extractor] Extracted 15 facts, 10 new entities (confidence range: 0.78-0.98)",
    "[risk_analyzer] Analyzing 15 facts across 10 entities using Gemini (gemini-2.0-flash)...",
    "[risk_analyzer] Identified 4 risk flags (severity range: 4-5/5)",
    "[query_refiner] Iteration 1 — evaluating coverage gaps...",
    "[query_refiner] Found 6 uninvestigated entities: Hansueli Overturf, Redwood Capital Bancorp, Joseppi's LLC...",
    "[query_refiner] Generated 5 refined queries targeting family connections and related entities",
    "[search_executor] Executing 5 refined queries via Tavily...",
    "[search_executor] ✓ 'Hansueli Hans Overturf FINRA suspension CRD 4138916' — 6 results",
    "[search_executor] ✓ 'Sisu Capital California DFPI enforcement revocation' — 5 results",
    "[search_executor] ✓ 'Overturf Financial Services Mill Valley enforcement' — 4 results",
    "[search_executor] ✓ 'Joseppi LLC Arcata Theatre Lounge NLRB complaint' — 5 results",
    "[search_executor] ✓ 'Redwood Capital Bancorp RWCB unauthorized trading SEC' — 3 results",
    "[search_executor] Search complete: 23 results from 5 queries in 2.7s",
    "[fact_extractor] Extracted 18 additional facts, 8 new entities (confidence range: 0.78-0.97)",
    "[risk_analyzer] Analyzing 33 facts across 18 entities...",
    "[risk_analyzer] Identified 3 additional risk flags (severity range: 3-5/5)",
    "[query_refiner] Iteration 2 — evaluating coverage gaps...",
    "[query_refiner] Found 5 uninvestigated entities: Morgan Stanley, Noir Execution Inc, Judge Corley...",
    "[query_refiner] Generated 4 refined queries targeting court records and shell companies",
    "[search_executor] Executing 4 refined queries via Tavily...",
    "[search_executor] ✓ 'SEC v Sisu Capital 3:23-cv-03855 NDCA docket' — 4 results",
    "[search_executor] ✓ 'Noir Execution Inc California corporation Timothy Overturf' — 2 results",
    "[search_executor] ✓ 'KlaymanToskes Timothy Overturf investigation' — 3 results",
    "[search_executor] ✓ 'Hansueli Overturf Redwood Parks Lodge fraud 2004' — 3 results",
    "[search_executor] Search complete: 12 results from 4 queries in 2.1s",
    "[fact_extractor] Extracted 12 additional facts, 8 new entities (confidence range: 0.80-0.95)",
    "[risk_analyzer] Final analysis: 45 facts across 26 entities...",
    "[risk_analyzer] Identified 1 additional risk flag. Total: 8 risk flags (severity range: 3-5/5)",
    "[query_refiner] Iteration 3 — sufficient coverage achieved. Proceeding to report generation.",
    "[report_generator] Generating comprehensive due diligence report using Gemini...",
    "[report_generator] Report complete — 9 sections, CRITICAL overall risk rating",
    "[graph_builder] Storing 26 entities and 45 relationships in graph database...",
    "[graph_builder] Computing analytics: degree centrality, betweenness centrality, community detection...",
    "[graph_builder] Built identity graph with 26 nodes, 38 edges → outputs/graphs/Timothy_Overturf_identity_graph.html",
    "✅ Investigation complete — 45 facts, 26 entities, 8 risk flags, 3 iterations",
]

# Pipeline node sequence for simulating progress
DEMO_PIPELINE_STEPS = [
    ("query_planner", 0, 0.04),
    ("search_executor", 0, 0.12),
    ("fact_extractor", 0, 0.20),
    ("risk_analyzer", 0, 0.28),
    ("query_refiner", 1, 0.34),
    ("search_executor", 1, 0.44),
    ("fact_extractor", 1, 0.52),
    ("risk_analyzer", 1, 0.60),
    ("query_refiner", 2, 0.66),
    ("search_executor", 2, 0.74),
    ("fact_extractor", 2, 0.82),
    ("risk_analyzer", 2, 0.87),
    ("query_refiner", 3, 0.90),
    ("report_generator", 3, 0.94),
    ("graph_builder", 3, 0.98),
]
