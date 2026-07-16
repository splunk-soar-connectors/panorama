**Unreleased**

* Prevent threat PCAP filenames from escaping the per-action temporary directory.
* Escape XML elements and reject unsafe XPath literal characters in URL, application, and address values.
* Validate independent name and destination parameters before constructing Panorama policy paths.
* Verify Panorama server certificates by default while retaining the explicit asset opt-out.
* Exclude the Panorama API key from commit-request debug output.
* Bound commit and query polling and fail on undocumented Panorama job states.
