**Unreleased**

* Bound threat PCAP downloads by the configured SOAR vault attachment limit.
* Normalized internationalized URL hostnames before adding or removing Panorama block entries.
* Respected the commit opt-out when blocking URLs on PAN-OS 8 and earlier.
* Returned actionable errors instead of crashing when credential generation or response parsing fails.
