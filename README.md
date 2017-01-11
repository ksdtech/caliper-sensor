# caliper-python-example

Test project to imagine a "sensor" that would work with our school district's
PowerSchool SIS and place assessment data into a searchable warehouse.

This example was built in Python 3 with IMS Global's
[Python Caliper Analytics™ sensor library](https://github.com/IMSGlobal/caliper-python-public)

The sample script, `send_outcome.py` tries to emulate the "Example Assessment Sequence"
described in the
[IMS Caliper Analytics™ Implementation Guide](https://www.imsglobal.org/caliper/caliperv1p0/ims-caliper-analytics-implementation-guide).

For a backend, I'm using [Apache CouchDB](http://couchdb.apache.org/).
One click install for Mac.  Open CouchDB, create a database named
"caliper_events". Then use

```
host='http://127.0.0.1:5984/caliper_events/'
```

in the configuration in `send_outcome.py`.

Some examples of `mango` CouchDB queries can be found in
[couchdb.md](couchdb.md).
