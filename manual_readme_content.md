[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2022 Splunk Inc."
[comment]: # ""
[comment]: # "  Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
### Overview

The Panorama app has been tested with PanOS version 7.0.4 and should work with any version above.

All the containment actions (like **block ip** etc.), take a policy name and the policy type as
parameters. The action first creates an object (Application Group, Address Group, etc.) on the
Panorama device to represent the object being blocked. This object is then added to the specified
policy. It does not modify any other policy parameters including the **Action** . Therefore you must
pre-configure the policy action as **Drop** .

Most of the actions execute a commit on the panorama device followed by a commit on the device
group. This second commit results in Panorama sending the commit to each device that belongs to a
device group, which could take some time. It is a good idea to add a time interval between two
panorama actions when executing a playbook

Panorama restricts object names to 31 characters. This could result in object names that are created
by Phantom being truncated in some cases.

It is usually a good idea to have one Policy created on the Panorama device to handle the **block**
of each type of object. The panorama_app playbook that is available on the community github repo
assumes this type of configuration. Note that to block URLs on Panorama, they are included in a URL
Filtering profile that is usually added to an **Allow** policy. Please see the PanOS documentation
for more details.

### Commit Configuration

You can use the commit API request to commit a candidate configuration to a firewall. Commit actions
are called at the end of all Contain actions (e.g. BlockIP).

You can learn more about Commit Configuration below: (API)

-   [Commit and
    Commit-All](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api.html)
-   [Panorama Commit Operations - Learn about Partial
    commits](https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-web-interface-help/panorama-web-interface/panorama-commit-operations.html)

### Audit Comment Archive

If the option "Require audit comment on policies" (Panorama -> Management) is enabled, Audit
comments must be specified to a given Policy rule before committing any changes to that rule.

WARNING: Additionally, the length of an Audit comment can be at most 256 characters.

You can learn more about Audit comment below:

-   [Audit Comment
    Archive](https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-web-interface-help/policies/audit-comment-archive.html)
-   [Making changes to Audit comments via
    API](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/run-operational-mode-commands-api.html)