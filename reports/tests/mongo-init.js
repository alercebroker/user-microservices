db.createCollection('test')
db.reports.insertMany([
  {
    date: new ISODate("2023-01-01T00:00:00Z"),
    object: "OBJECT1",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user1"
  },
  {
    date: new ISODate("2023-01-01T12:00:00Z"),
    object: "OBJECT1",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user2"
  },
  {
    date: new ISODate("2023-01-02T12:00:00Z"),
    object: "OBJECT1",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user4"
  },
  {
    date: new ISODate("2023-01-01T12:00:00Z"),
    object: "OBJECT2",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user1"
  },
  {
    date: new ISODate("2023-01-01T12:00:00Z"),
    object: "OBJECT2",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "Bogus",
    owner: "user2"
  },
  {
    date: new ISODate("2023-01-01T18:00:00Z"),
    object: "OBJECT2",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user4"
  },
  {
    date: new ISODate("2023-01-02T00:00:00Z"),
    object: "OBJECT3",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "Bogus",
    owner: "user1"
  },
  {
    date: new ISODate("2023-01-02T00:00:00Z"),
    object: "OBJECT3",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user2"
  },
  {
    date: new ISODate("2023-01-02T12:00:00Z"),
    object: "OBJECT3",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user3"
  },
  {
    date: new ISODate("2023-01-03T12:00:00Z"),
    object: "OBJECT4",
    solved: false,
    source: "source1",
    observation: "obs1",
    report_type: "TOM",
    owner: "user3"
  },
])
