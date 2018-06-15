ldif-csv-conv — LDIF to CSV and vice versa
==========================================

These two scripts can convert datasets between the LDIF (LDAP Data Interchange
Format) and CSV (Comma-Separated Values) formats, in both directions, without
losing information.  
(Comments in the LDIF are not preserved; ordering of multi-value attributes is
preserved.)

## LDIF to CSV

    ./ldif2csv data.ldif > data.csv

or

    ./ldif2csv < data.ldif > data.csv

## CSV to LDIF

    ./csv2ldif data.csv > data.ldif

or

    ./csv2ldif < data.csv > data.ldif

## Notes (format, etc)

* The CSV files use `;` as the cell separator, enclose all cells in `"` (with
  `"`s in the input represented as `""`) and separate the values of a
  multi-value attribute with `|`:

    "dn";"email";"objectclass"
    "uid=johndoe,dc=example,dc=com";"johndoe@example.com";"inetOrgPerson|top"

  The `""` escaping allows you to use both `;` and `"` in your data. If you
  need to use `|`, you'll have to edit the `JOINER` definition in both script
  files.  
  `ldif2csv` will examine your data and output suggestions for unused
  characters that could be used as joiners or delimiters.

* Individual attribute values¹ longer than 499 bytes (think `jpegphoto`s) are
  split off into individual files to keep the CSV small.  
  They are referenced as `FILE=dn=…,attr=…,id=…` in the respective CSV cell. If
  this format is kept intact, they will be reintegrated into the LDIF by
  `csv2ldif`.  
  The user is free to manually insert or modify these `FILE=…` references — if
  they point to a valid file, they will be followed; if not, the converter will
  crash and burn. Enjoy!  
  (¹ Note that this means you can have a mixture of "direct" and "referenced"
  values in the same cell.)

## Known issues

* Conversion from CSV to LDIF is very slow when the input contains a lot of
  binary data (e.g. `jpegphoto` attributes).
* *Error handling? What's that?*  
  If something goes wrong, you'll get your usual Python exception stack trace.
