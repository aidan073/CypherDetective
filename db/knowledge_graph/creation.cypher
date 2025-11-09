// --- Clear existing data
MATCH (n) DETACH DELETE n;

// === Create Victim ===
CREATE (victim:Victim {
    name: "John Doe",
    blood_type: "A+"
});

// === Create Locations ===
CREATE
    (hotel:Location {name: "Grandview Hotel", type: "hotel"}),
    (building:Location {name: "Victim's Apartment Building", type: "residential"}),
    (outside:Location {name: "Outside", type: "outdoors"});

// === Create Banks ===
CREATE
    (b1:Bank {name: "First National"}),
    (b2:Bank {name: "River City Bank"}),
    (b3:Bank {name: "Metro Credit Union"});

// === Create 10 Suspects ===
CREATE
(s1:Suspect {name: "Alice Brown", verified_alibi: true, hair: "blonde", height: 5.7, blood_type: "B+", employee: false, access_level: 0, total_deposits: 12000}),
(s2:Suspect {name: "Ben Carter", verified_alibi: false, hair: "brown", height: 6.1, blood_type: "O+", employee: false, access_level: 0, total_deposits: 475500}),
(s3:Suspect {name: "Chloe Diaz", verified_alibi: false, hair: "red", height: 5.5, blood_type: "A-", employee: true, access_level: 3, total_deposits: 23000}),
(s4:Suspect {name: "David Evans", verified_alibi: false, hair: "brown", height: 6.2, blood_type: "O+", employee: true, access_level: 2, total_deposits: 475500}),
(s5:Suspect {name: "Ella Fisher", verified_alibi: true, hair: "black", height: 5.6, blood_type: "AB-", employee: false, access_level: 0, total_deposits: 15000}),
(s6:Suspect {name: "Frank Green", verified_alibi: false, hair: "brown", height: 6.0, blood_type: "O+", employee: true, access_level: 1, total_deposits: 6000}),
(s7:Suspect {name: "Grace Hill", verified_alibi: false, hair: "brown", height: 6.0, blood_type: "O+", employee: true, access_level: 2, total_deposits: 475500}),
(s8:Suspect {name: "Harry Irving", verified_alibi: false, hair: "brown", height: 6.3, blood_type: "O+", employee: true, access_level: 2, total_deposits: 475500}),
(s9:Suspect {name: "Isla Jones", verified_alibi: false, hair: "brown", height: 6.0, blood_type: "B+", employee: true, access_level: 3, total_deposits: 450000}),
(s10:Suspect{name: "Jack Knight", verified_alibi: false, hair: "blonde", height: 6.1, blood_type: "O+", employee: false, access_level: 0, total_deposits: 475500});

// === Create Location Relationships ===
MATCH
  (hotel:Location {name: "Grandview Hotel"}),
  (building:Location {name: "Victim's Apartment Building"}),
  (outside:Location {name: "Outside"})
MATCH (s:Suspect)
FOREACH (_ IN CASE WHEN s.name IN ["Alice Brown", "Ben Carter", "Ella Fisher"] THEN [1] ELSE [] END | CREATE (s)-[:WAS_AT]->(building))
FOREACH (_ IN CASE WHEN s.name IN ["Chloe Diaz", "David Evans", "Frank Green", "Grace Hill", "Harry Irving", "Isla Jones"] THEN [1] ELSE [] END | CREATE (s)-[:WAS_AT]->(hotel))
FOREACH (_ IN CASE WHEN s.name = "Jack Knight" THEN [1] ELSE [] END | CREATE (s)-[:WAS_AT]->(outside));

// Employees (hotel workers)
MATCH (hotel:Location {name: "Grandview Hotel"})
MATCH (s:Suspect)
WHERE s.employee = true
CREATE (s)-[:WORKS_AT]->(hotel);

// === Victim Relationships ===
MATCH (v:Victim {name:"John Doe"}), (s:Suspect)
WHERE s.name IN ["David Evans", "Grace Hill", "Jack Knight"]
CREATE (s)-[:CLOSE_FRIEND_OF]->(v);

// === Bank Accounts ===
MATCH (b1:Bank {name:"First National"}), (b2:Bank {name:"River City Bank"}), (b3:Bank {name:"Metro Credit Union"})
MATCH (s:Suspect)
FOREACH (_ IN CASE WHEN s.total_deposits = 475500 THEN [1] ELSE [] END |
    CREATE (s)-[:HAS_ACCOUNT_AT]->(b1)
    CREATE (s)-[:HAS_ACCOUNT_AT]->(b2)
    CREATE (s)-[:HAS_ACCOUNT_AT]->(b3)
);