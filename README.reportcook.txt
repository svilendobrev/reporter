hi
here's the situation.

 - the thing is in gonna-be-production. 
 BUT it does not mean it's 100% stable, well-tested, documented, ... 
   the overall project (very entangled HR/relations/salary/timetracking/legislation system 
   etc) is in deathmarch for quite some time and these things are luxury; 
   on other hand i'm out of the company anymore 

 - it's a shared effort by me and a colleague, me being idea-generator and 
 big-picture/language architect, he being the implementor and everything 
 as of lately.

 - the idea of opensourcig is hanging since the beginning ~3 y ago 
 (we've put about 2+ man years into it...)

 - it needs some effort to get well-separated from the all-other-stuff, 
   mainly configs and facading interfaces, 
   and noone of us had the time to do it.

so... after i describe now in brief what it is/can/might be, u decide whether u
want to take the plunge and do the separation/fine-cuts; that is - i'll publish 
the source as is, and u (with my help) make it usable for anyone, still keeping 
it usable for the project it comes from - they have no time to change APIs.

so, the spec in brief:

 * a declarative language for describing a report:
  
   - input params (this is decl. only)

   - data extraction, depending on above + extras (this is DIY)

   - data processing - filtering, calcs, aggregation/grouping/ordering - this is the main thing, the report-model

   - output layout into various looks (like MVC) - console/plaintext, 
  wxwin/ printpreview, pdf/reportlab, html, excel, (not yet: xml, m$word, others...)

 * the modelling is discrete, that is the atomary item is a field. 
 then fields can be grouped freeform, rows, columns, whatever

 * there is inheritance in several aspects - structure, fields, processing, layout

 * there is containment (any field can be a sub-report)

 * various report-metamodels, depending on structural flexibility 
  - bunch-of-fields - free form
  - rows-of-fields - list of people
  - table - rows of (same) columns (tabular data)
  - cross-cut cols/rows (variable number rows * variable number columns)

example report:

class SprPeople( SprDef):
    class MyRow( Row):
        _set_ = FieldContainer( 
            name    = FldDef( type=Text, model='name.name',
                        view=FldView( label='Name', align='l', border='r')),
            age     = FldDef( type=Int, model='ageyears',
                        view=FldView( label='Възраст', align='r', border='r')),
            city    = FldDef( type=Text, model='address.city'),
            suburb = FldDef( type=Text, model='address.suburb'),
            )
        _calc_ = FieldContainer(
            address = FldDef( type=Text,
                        data=lambda r: r.city +' '+ r.suburb),
                        view=FldView( label='Addresse', align='l', border='r')),
                        )
        RowType = MyRow

