# XML Parser for OCR Scanned Case Files

*Author: Garrett Myers*

## Usage

### ROUTE: /

Returns a read me for the API, along with the API documentation.

### ROUTE: /cases

Returns a list of cases and their data.

### ROUTE: /cases/casename

Get cases by name.

The desired case should be placed into the url as follows:

ex. cases/TestCase

Cases are *not* unique. The get request may return multiple cases.

### ROUTE: /cases/new

Allows a user to upload a new case file to be parsed.

The post uses HTML form-data. Please provide the following inputs:

*casefile*: An **XML** file created by OCR scan of a case document.
*casename*: Name for the case to be referenced by.

The server will attempt to extract the plaintiff and defendant of the case from the XML file. It assumes a generic format of something like the following:

...............

COURT OF ......

*PLAINTIFF*....

V(S). .........

*DEFENDANT*....

DEFENDANT, ....

As such, depending on the OCR, extraneous data may be present in the results.

Upon success, the user is redirected to a get request for 'cases/casename'
