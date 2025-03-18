### Overview

The Panorama app has been tested with PanOS version 11.0.2 and should work with any version above.

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

- [Commit and
  Commit-All](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api.html)
- [Panorama Commit Operations - Learn about Partial
  commits](https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-web-interface-help/panorama-web-interface/panorama-commit-operations.html)

### Audit Comment Archive

If the option "Require audit comment on policies" (Panorama -> Management) is enabled, Audit
comments must be specified to a given Policy rule before committing any changes to that rule.

WARNING: Additionally, the length of an Audit comment can be at most 256 characters.

You can learn more about Audit comment below:

- [Audit Comment
  Archive](https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-web-interface-help/policies/audit-comment-archive.html)
- [Making changes to Audit comments via
  API](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/run-operational-mode-commands-api.html)

### Common parameter behavior

- Name\
  Address, Address group, EDL and Policy name must be alphanumeric and can contain only special characters like dot(.), hyphen(-), underscore(\_) and space( ) but cannot start with them. (up to 63 characters)

  - Examples:
    - Test_name (valid input)
    - \_Addressname (invalid input)

- Device group\
  The **device_group** must be alphanumeric and can contain only special characters like dot(.), hyphen(-), underscore(\_) and space( ) but cannot start with them. (up to 31 characters)

  - Examples:
    - Test_edl (valid input)
    - \_Testedl (invalid input)

- disable_override\
  When the **device_group** is 'shared' the **disable_override** parameter is ignored.

- should_commit_changes (Default: true)\
  When the **should_commit_changes** is set to **true**, This commits both, changes to the firewall and changes to the device groups at the end of this action.

- use_partial_commit\
  When **use_partial_commit** is **true**, this performs user specific commit. As part of the request, the configuration's username is included as the administrator name. When the **should_commit_changes** is **false** the **use_partial_commit** parameter is ignored.

**Note**

- If you want to add below special characters in any of the field you need to add as per below list.

  - & - **`&amp;`**
  - < - **`&lt;`**
  - \> - **`&gt;`**
  - " - **`&quot;`**
  - ' - **`&apos;`**

- Example:
  If you want to pass value as -> testing&\
  In the parameter pass it as -> testing`&amp;`
