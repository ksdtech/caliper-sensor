# CouchDB backend

## Queries

### Find all OutcomeEvents

And return only the attempt, assignment, student, dates, comment and score:
```
{
    "selector": {
        "data": {
            "@type": {
                "$eq": "http://purl.imsglobal.org/caliper/v1/OutcomeEvent"
            }
        }
    },
    "fields": [
        "data.object.@id",
        "data.object.assignable",
        "data.object.actor",
        "data.object.startedAtTime",
        "data.object.endedAtTime",
        "data.generated.comment",
        "data.generated.normalScore"
    ]
}
```

### Find all events related to student 123456
```
{
    "selector": {
        "data": {
            "generated": {
                "actor": {
                    "$eq": "https://kentfieldschools.org/student/123456"
                }
            }
        }
    }
}
```

## Find all events for an assignment
```
{
    "selector": {
        "data": {
            "generated": {
                "assignable": {
                    "$eq": "https://kentfieldschools.org/year/1617/school/104/course/7177/section/4/assessment/44001"
                }
            }
        }
    }
}
```
