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

// === Create 10 Suspects ===
CREATE
(s1:Suspect {
    name: "Alice Brown",
    verified_alibi: true,
    hair: "blonde",
    height: 5.7,
    blood_type: "B+",
    access_level: 0,
    graph_0: true
}),
(s2:Suspect {
    name: "Ben Carter",
    verified_alibi: true,
    hair: "brown",
    height: 6.1,
    blood_type: "O+",
    access_level: 0,
    graph_0: true
}),
(s3:Suspect {
    name: "Chloe Diaz",
    verified_alibi: false,
    hair: "red",
    height: 5.5,
    blood_type: "A-",
    access_level: 3,
    graph_0: true, graph_1: true, graph_2: true, graph_3: true, graph_4: true
}),
(s4:Suspect {
    name: "David Evans",
    verified_alibi: false,
    hair: "brown",
    height: 6.2,
    blood_type: "O+",
    access_level: 2,
    graph_0: true, graph_1: true, graph_2: true, graph_3: true, graph_4: true, graph_5: true, graph_6: true, graph_7: true, graph_8: true
}),
(s5:Suspect {
    name: "Ella Fisher",
    verified_alibi: true,
    hair: "black",
    height: 5.6,
    blood_type: "AB-",
    access_level: 0,
    graph_0: true, graph_1: true
}),
(s6:Suspect {
    name: "Frank Green",
    verified_alibi: false,
    hair: "brown",
    height: 6.0,
    blood_type: "O+",
    access_level: 1,
    graph_0: true, graph_1: true, graph_2: true, graph_3: true
}),
(s7:Suspect {
    name: "Grace Hill",
    verified_alibi: false,
    hair: "brown",
    height: 6.0,
    blood_type: "O+",
    access_level: 2,
    graph_0: true, graph_1: true, graph_2: true, graph_3: true, graph_4: true, graph_5: true, graph_6: true, graph_7: true
}),
(s8:Suspect {
    name: "Harry Irving",
    verified_alibi: false,
    hair: "brown",
    height: 6.3,
    blood_type: "O+",
    access_level: 2,
    graph_0: true, graph_1: true, graph_2: true, graph_3: true, graph_4: true, graph_5: true, graph_6: true
}),
(s9:Suspect {
    name: "Isla Jones",
    verified_alibi: false,
    hair: "brown",
    height: 6.0,
    blood_type: "B+",
    access_level: 3,
    graph_0: true, graph_1: true, graph_2: true, graph_3: true, graph_4: true, graph_5: true
}),
(s10:Suspect {
    name: "Jack Knight",
    verified_alibi: false,
    hair: "blonde",
    height: 6.1,
    blood_type: "O+",
    access_level: 0,
    graph_0: true, graph_1: true, graph_2: true
});

// === Create Location Relationships ===
MATCH
  (hotel:Location {name: "Grandview Hotel"}),
  (building:Location {name: "Victim's Apartment Building"}),
  (outside:Location {name: "Outside"})
MATCH (s:Suspect)
FOREACH (_ IN CASE WHEN s.name IN ["Alice Brown", "Ella Fisher"] THEN [1] ELSE [] END | CREATE (s)-[:WAS_AT]->(building))
FOREACH (_ IN CASE WHEN s.name IN ["Chloe Diaz", "David Evans", "Frank Green", "Grace Hill", "Harry Irving", "Isla Jones"] THEN [1] ELSE [] END | CREATE (s)-[:WAS_AT]->(hotel))
FOREACH (_ IN CASE WHEN s.name IN ["Jack Knight", "Ben Carter"] THEN [1] ELSE [] END | CREATE (s)-[:WAS_AT]->(outside));

// Employees (hotel workers)
MATCH (hotel:Location {name: "Grandview Hotel"})
MATCH (s:Suspect)
WHERE s.access_level > 0
CREATE (s)-[:WORKS_AT]->(hotel);

// === Victim Relationships ===
MATCH (v:Victim {name:"John Doe"}), (s:Suspect)
WHERE s.name IN ["David Evans", "Grace Hill", "Jack Knight"]
CREATE (s)-[:CLOSE_FRIEND_OF]->(v);

// === Create Banks ===
CREATE
(b1:Bank {name: "First National", graph_7: true}),
(b2:Bank {name: "River City Bank", graph_7: true}),
(b3:Bank {name: "Metro Credit Union", graph_7: true});

// === Create Deposit Relationships with Amounts ===

// Alice Brown: total = 275
MATCH (b1:Bank {name: "First National"}), (s1:Suspect {name: "Alice Brown"})
CREATE (s1)-[:DEPOSITED_IN {amount: 275,  date: date("2025-10-09")}]->(b1);

// Ben Carter: total = 450
MATCH (b1:Bank {name: "First National"}), (s2:Suspect {name: "Ben Carter"})
CREATE (s2)-[:DEPOSITED_IN {amount: 450,  date: date("2025-10-14")}]->(b1);

// Chloe Diaz: total = 5,120
MATCH (b1:Bank {name: "First National"}), (s3:Suspect {name: "Chloe Diaz"})
CREATE (s3)-[:DEPOSITED_IN {amount: 5120,  date: date("2025-10-13")}]->(b1);

// David Evans: total = 475,500
MATCH (b1:Bank {name: "First National"}), (s4:Suspect {name: "David Evans"})
CREATE (s4)-[:DEPOSITED_IN {amount: 200000, date: date("2025-10-10")}]->(b1);
MATCH (b2:Bank {name: "River City Bank"}), (s4:Suspect {name: "David Evans"})
CREATE (s4)-[:DEPOSITED_IN {amount: 150000, date: date("2025-10-15")}]->(b2);
MATCH (b3:Bank {name: "Metro Credit Union"}), (s4:Suspect {name: "David Evans"})
CREATE (s4)-[:DEPOSITED_IN {amount: 125500, date: date("2025-10-20")}]->(b3);

// Grace Hill: total = 320,500
MATCH (b1:Bank {name: "First National"}), (s7:Suspect {name: "Grace Hill"})
CREATE (s7)-[:DEPOSITED_IN {amount: 120000, date: date("2025-10-11")}]->(b1);
MATCH (b2:Bank {name: "River City Bank"}), (s7:Suspect {name: "Grace Hill"})
CREATE (s7)-[:DEPOSITED_IN {amount: 150000, date: date("2025-10-16")}]->(b2);
MATCH (b3:Bank {name: "Metro Credit Union"}), (s7:Suspect {name: "Grace Hill"})
CREATE (s7)-[:DEPOSITED_IN {amount: 50500,  date: date("2025-10-23")}]->(b3);

// Harry Irving: total = 7,860
MATCH (b1:Bank {name: "First National"}), (s8:Suspect {name: "Harry Irving"})
CREATE (s8)-[:DEPOSITED_IN {amount: 7860, date: date("2025-10-18")}]->(b1);

// Jack Knight: total = 112,450
MATCH (b1:Bank {name: "First National"}), (s10:Suspect {name: "Jack Knight"})
CREATE (s10)-[:DEPOSITED_IN {amount: 100000, date: date("2025-10-12")}]->(b1);
MATCH (b2:Bank {name: "River City Bank"}), (s10:Suspect {name: "Jack Knight"})
CREATE (s10)-[:DEPOSITED_IN {amount: 12450,  date: date("2025-10-17")}]->(b2);