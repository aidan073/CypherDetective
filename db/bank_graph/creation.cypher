// --- Clear everything first
MATCH (n) DETACH DELETE n;

// === Create Suspects ===
CREATE
(david:Suspect {name: "David Evans"}),
(grace:Suspect {name: "Grace Hill"});

// === Create Banks ===
CREATE
(b1:Bank {name: "First National"}),
(b2:Bank {name: "River City Bank"}),
(b3:Bank {name: "Metro Credit Union"});

// === Create Deposit Relationships with Amounts ===
// David Evans: total = 475,500
CREATE (david)-[:DEPOSITED_IN {amount: 200000, date: date("2025-10-10")}]->(b1);
CREATE (david)-[:DEPOSITED_IN {amount: 150000, date: date("2025-10-15")}]->(b2);
CREATE (david)-[:DEPOSITED_IN {amount: 125500, date: date("2025-10-20")}]->(b3);

// Grace Hill: total = 320,000
CREATE (grace)-[:DEPOSITED_IN {amount: 120000, date: date("2025-10-11")}]->(b1);
CREATE (grace)-[:DEPOSITED_IN {amount: 150000, date: date("2025-10-16")}]->(b2);
CREATE (grace)-[:DEPOSITED_IN {amount: 50000,  date: date("2025-10-23")}]->(b3);