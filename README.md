[comment]: # "Auto-generated SOAR connector documentation"
# Panorama

Publisher: Splunk  
Connector Version: 5.0.0  
Product Vendor: Palo Alto Networks  
Product Name: Panorama  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 6.1.0  

This app integrates with the Palo Alto Networks Panorama product to support several containment and investigative actions

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2023 Splunk Inc."
[comment]: # ""
[comment]: # "  Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
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

### Common parameter behavior

- Name   
 Address, Address group, EDL and Policy name must be alphanumeric and can contain only special characters like dot(.), hyphen(-), underscore(_) and space( ) but cannot start with them. (up to 63 characters)  
    - Examples:  
        - Test_name (valid input)  
        - _Addressname (invalid input)  

- Device group  
 The **device_group** must be alphanumeric and can contain only special characters like dot(.), hyphen(-), underscore(_) and space( ) but cannot start with them. (up to 31 characters) 
    - Examples:  
      - Test_edl (valid input)  
      - _Testedl (invalid input)  

- disable_override  
 When the **device_group** is 'shared' the **disable_override** parameter is ignored. 

- should_commit_changes (Default: true)  
 When the **should_commit_changes** is set to **true**, This commits both, changes to the firewall and changes to the device groups at the end of this action. 

- use_partial_commit  
 When **use_partial_commit** is **true**, this performs user specific commit. As part of the request, the configuration's username is included as the administrator name. When the **should_commit_changes** is **false** the **use_partial_commit** parameter is ignored.


 **Note**  
 - If you want to add below special characters in any of the field you need to add as per below list.  
    - & - **`&amp;`**  
    - < - **`&lt;`**  
    - \> - **`&gt;`**  
    - " - **`&quot;`**  
    - ' - **`&apos;`**  

- Example:
 If you want to pass value as  -> testing&  
 In the parameter pass it as -> testing`&amp;`


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Panorama asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device** |  required  | string | Device IP/Hostname
**verify_server_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Username
**password** |  required  | password | Password

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity  
[block url](#action-block-url) - Block an URL  
[unblock url](#action-unblock-url) - Unblock an URL  
[block application](#action-block-application) - Block an application  
[unblock application](#action-unblock-application) - Unblock an application  
[block ip](#action-block-ip) - Block an IP  
[unblock ip](#action-unblock-ip) - Unblock an IP  
[list applications](#action-list-applications) - List the applications that the device knows about and can block  
[run query](#action-run-query) - Run a query on Panorama  
[commit changes](#action-commit-changes) - Commit changes to the firewall and device groups  
[get threat pcap](#action-get-threat-pcap) - Export a Threat PCAP file  
[list edl](#action-list-edl) - List External Dynamic Lists  
[get edl](#action-get-edl) - Get data of an External Dynamic List  
[create edl](#action-create-edl) - Create an External Dynamic List  
[modify edl](#action-modify-edl) - Modify an External Dynamic List  
[delete edl](#action-delete-edl) - Delete an External Dynamic List  
[create policy](#action-create-policy) - Create a security policy rule  
[custom block policy](#action-custom-block-policy) - Block IP addresses, Address Groups, EDLs(External Dynamic List), Applications, or URL Categories in Panorama and creates a custom uni-directional (direction parameter value as from or to) or bi-directional (direction parameter value as both) security rule  
[modify policy](#action-modify-policy) - Modify a security policy rule  
[move policy](#action-move-policy) - Move a security policy rule  
[delete policy](#action-delete-policy) - Delete a security policy rule  
[create address group](#action-create-address-group) - Create an address group  
[modify address group](#action-modify-address-group) - Modify an address group  
[list address groups](#action-list-address-groups) - List the address groups  
[get address group](#action-get-address-group) - Fetch address group details for the supplied address group name  
[delete address group](#action-delete-address-group) - Delete an address group for the supplied address group name  
[create address](#action-create-address) - Create an address on the panorama platform  
[get address](#action-get-address) - Fetch address details for the supplied address name  
[delete address](#action-delete-address) - Delete address details for the supplied address name  

## action: 'test connectivity'
Validate the asset configuration for connectivity

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'block url'
Block an URL

Type: **contain**  
Read only: **False**

This action does the following to block a URL:<ul><li>Create an URL Filtering profile object named '<b>Phantom URL List for [device_group]</b>' containing the URL to block.</br>If the profile is already present, then it will be updated to include the URL to block. IMPORTANT: For Version 9 and above, a URL Filtering profile no longer includes allow-list/block-list. The official workaround is to use a Custom URL category instead. Therefore, we create a new Custom URL category with the same name as the profile and link it to the profile. Then, We configure the profile to block the URL category on both 'SITE ACCESS' and 'USER CREDENTIAL SUBMISSION' columns.</li><li>If a <b>policy_name</b> is provided, re-configure the policy (specified in the <b>policy_name</b> parameter) to use the created URL Filtering profile. The URL filtering profile created in the previous step will be linked to the Profile Settings of the specified policy.</br>If the policy is not found on the device, the action will return an error.</li><li>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to block | string |  `url` 
**device_group** |  required  | Device group in which you want to block url | string |  `panorama device group` 
**policy_type** |  optional  | Block policy type | string | 
**policy_name** |  optional  | Policy to use | string |  `panorama policy name` 
**audit_comment** |  optional  | Audit comment to be used with the policy name. Maximum 256 characters | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.audit_comment | string |  |   updated description 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.policy_name | string |  `panorama policy name`  |   test_policy 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.url | string |  `url`  |   https://www.test.com 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.does_policy_exist.response.@code | string |  |   19 
action_result.summary.does_policy_exist.response.result.entry.to.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.to.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.to.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.to.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.to.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.tag.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.#text | string |  |   test_tag 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.@loc | string |  |   do_not_delete_dg_default 
action_result.summary.does_policy_exist.response.result.entry.from.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.from.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.from.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.from.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.@name | string |  |   test_playbook_policy 
action_result.summary.does_policy_exist.response.result.entry.@time | string |  |   2023/10/03 23:44:32 
action_result.summary.does_policy_exist.response.result.entry.@uuid | string |  |   6eca9cdf-2c3b-4dc8-bf8b-4b967f4519fa 
action_result.summary.does_policy_exist.response.result.entry.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action.#text | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.action.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.action.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.#text | string |  |   12.23.34.45 
action_result.summary.does_policy_exist.response.result.entry.source.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.service.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.service.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.service.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.service.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.service.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.category.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.category.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.category.member.#text | string |  |   auctions 
action_result.summary.does_policy_exist.response.result.entry.category.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.category.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.category.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.category.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.rule-type.#text | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.application.@time | string |  |   2023/10/03 23:44:32 
action_result.summary.does_policy_exist.response.result.entry.application.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.#text | string |  |   3pc 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.application.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.description.#text | string |  |   Test playbook policy 
action_result.summary.does_policy_exist.response.result.entry.description.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.description.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.description.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.#text | string |  |   23.34.45.67 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.@count | string |  |   1 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   1 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.set_url_filtering.response.msg | string |  |   command succeeded 
action_result.summary.set_url_filtering.response.@code | string |  |   20 
action_result.summary.set_url_filtering.response.@status | string |  |   success 
action_result.summary.update_audit_comment.response.result | string |  |   Successfully added comment for xpath 
action_result.summary.update_audit_comment.response.@status | string |  |   success 
action_result.summary.update_security_policy.response.msg | string |  |   command succeeded 
action_result.summary.update_security_policy.response.@code | string |  |   20 
action_result.summary.update_security_policy.response.@status | string |  |   success 
action_result.summary.add_url_to_url_category.response.msg | string |  |   command succeeded 
action_result.summary.add_url_to_url_category.response.@code | string |  |   20 
action_result.summary.add_url_to_url_category.response.@status | string |  |   success 
action_result.summary.commit_config.finished_job.id | string |  |   10361 
action_result.summary.commit_config.finished_job.tdeq | string |  |   03:18:37 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/09/25 03:18:37 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/09/25 03:18:59 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.queued | string |  |   NO 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.warnings | string |  |  
action_result.summary.commit_config.finished_job.stoppable | string |  |   no 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   10362 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   03:19:02 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/09/25 03:19:02 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/09/25 03:19:02 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   test 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   NO 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   no 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.does_policy_exist.response.result.entry.to.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.action | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.source.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.target.negate | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.service.member | string |  |   application-default 
action_result.summary.does_policy_exist.response.result.entry.category.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-user.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@time | string |  |   2023/09/26 05:00:06 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.#text | string |  |   Phantom URL List for Shared 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@time | string |  |   2023/09/26 05:00:06 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@dirtyId | string |  |   23 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@dirtyId | string |  |   23 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/09/26 05:02:10 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   FAIL 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit failed 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   05:01:40 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   3054 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   error 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.#text | string |  |   23.34.45.67 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.disabled.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.disabled.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.disabled.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.disabled.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.negate-source.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.#text | string |  |   12.23.34.45 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.group.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.group.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.group.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.member | string |  |   test_tag 
action_result.summary.does_policy_exist.response.result.entry.disabled | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.rule-type | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.description | string |  |   Test playbook policy 
action_result.summary.does_policy_exist.response.result.entry.negate-source | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles | string |  |  
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-destination | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.target.@time | string |  |   2023/10/09 05:23:34 
action_result.summary.does_policy_exist.response.result.entry.target.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.target.negate.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.target.negate.@time | string |  |   2023/10/09 05:23:34 
action_result.summary.does_policy_exist.response.result.entry.target.negate.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.target.negate.@dirtyId | string |  |   13 
action_result.summary.does_policy_exist.response.result.entry.target.@dirtyId | string |  |   13 
action_result.summary.does_policy_exist.response.result.entry.application.member.#text | string |  |   2ch 
action_result.summary.does_policy_exist.response.result.entry.application.member.@time | string |  |   2023/10/09 05:23:34 
action_result.summary.does_policy_exist.response.result.entry.application.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.@dirtyId | string |  |   13 
action_result.summary.does_policy_exist.response.result.entry.source-user.@time | string |  |   2023/10/09 05:23:34 
action_result.summary.does_policy_exist.response.result.entry.source-user.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@time | string |  |   2023/10/09 05:23:34 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@dirtyId | string |  |   13 
action_result.summary.does_policy_exist.response.result.entry.source-user.@dirtyId | string |  |   13 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member | string |  |   Phantom URL List for do_not_del 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'unblock url'
Unblock an URL

Type: **correct**  
Read only: **False**

For Version 8 and below, this action will remove the URL from the URL Filtering profile that was created/updated in the <b>block url</b> action. For Version 9 and above, this action will remove the URL from the Custom URL category that was created/updated in the <b>block url</b> action. If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to unblock | string |  `url` 
**device_group** |  required  | Device group in which you want to unblock url | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.url | string |  `url`  |   www.test.com 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.delete_url_from_url_category.response.msg | string |  |   command succeeded 
action_result.summary.delete_url_from_url_category.response.@code | string |  |   20 
action_result.summary.delete_url_from_url_category.response.@status | string |  |   success 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'block application'
Block an application

Type: **contain**  
Read only: **False**

This action does the following to block an application:<ul><li>Create an Application group named '<b>Phantom App List for [device_group]</b>' containing the application to block.</br>If the group is already present, then it will be updated to include the application.</li><li>If a <b>policy_name</b> is provided, re-configure the policy (specified in the <b>policy_name</b> parameter) to use the created application group.</br>If the policy is not found on the device, the action will return an error.</li><li>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.</li></ul>To get a list of applications that can be blocked, execute the <b>list applications</b> action.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**application** |  required  | Application to block | string |  `network application` 
**device_group** |  required  | Device group in which you want to block application | string |  `panorama device group` 
**policy_type** |  optional  | Block policy type | string | 
**policy_name** |  optional  | Policy to use | string |  `panorama policy name` 
**audit_comment** |  optional  | Audit comment to be used with the policy name. Maximum 256 characters | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.application | string |  `network application`  |   1c-enterprise 
action_result.parameter.audit_comment | string |  |   updated description 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.policy_name | string |  `panorama policy name`  |   test_policy 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.add_application_to_application_group.response.msg | string |  |   command succeeded 
action_result.summary.add_application_to_application_group.response.@code | string |  |   20 
action_result.summary.add_application_to_application_group.response.@status | string |  |   success 
action_result.summary.commit_config.finished_job.id | string |  |   2847 
action_result.summary.commit_config.finished_job.tdeq | string |  |   02:34:37 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/09/26 02:34:37 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/09/26 02:35:02 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.queued | string |  |   NO 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_config.finished_job.stoppable | string |  |   no 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.does_policy_exist.response.@code | string |  |   19 
action_result.summary.does_policy_exist.response.result.entry.to.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.to.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.to.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.to.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.to.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.@loc | string |  |   test 
action_result.summary.does_policy_exist.response.result.entry.from.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.from.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.from.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.from.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.@name | string |  |   test_pre_rule 
action_result.summary.does_policy_exist.response.result.entry.@time | string |  |   2023/09/26 02:29:58 
action_result.summary.does_policy_exist.response.result.entry.@uuid | string |  |   e97777da-aad8-44e0-9206-492172b9d18e 
action_result.summary.does_policy_exist.response.result.entry.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action.#text | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.action.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.action.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.source.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.source.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.source.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.target.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.target.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.target.negate.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.target.negate.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.target.negate.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.target.negate.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.target.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.service.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.service.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.#text | string |  |   application-default 
action_result.summary.does_policy_exist.response.result.entry.service.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.service.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.service.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.category.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.category.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.category.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.category.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.category.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.category.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.category.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.rule-type.#text | string |  |   intrazone 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.application.@time | string |  |   2023/09/26 02:29:58 
action_result.summary.does_policy_exist.response.result.entry.application.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.#text | string |  |   3pc 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.application.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.destination.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.destination.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.source-user.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.source-user.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.source-user.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@time | string |  |   2023/09/26 02:26:52 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@dirtyId | string |  |   15 
action_result.summary.does_policy_exist.response.result.@count | string |  |   1 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   1 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   2858 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   02:35:03 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/09/26 02:35:03 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/09/26 02:35:03 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   test 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   NO 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   no 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.update_audit_comment.response.result | string |  |   Successfully added comment for xpath 
action_result.summary.update_audit_comment.response.@status | string |  |   success 
action_result.summary.update_security_policy.response.msg | string |  |   command succeeded 
action_result.summary.update_security_policy.response.@code | string |  |   20 
action_result.summary.update_security_policy.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result.entry.application.member.#text | string |  |   airdroid 
action_result.summary.does_policy_exist.response.result.entry.application.member.@time | string |  |   2023/09/26 02:58:38 
action_result.summary.does_policy_exist.response.result.entry.application.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.@dirtyId | string |  |   19 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/09/26 03:00:03 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   FAIL 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit failed 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   02:59:33 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   2893 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   error 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.to.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.action | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.source.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.target.negate | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.service.member | string |  |   application-default 
action_result.summary.does_policy_exist.response.result.entry.category.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-user.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.tag.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.tag.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.#text | string |  |   test_tag 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.#text | string |  |   12.23.34.45 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.description.#text | string |  |   Test playbook policy 
action_result.summary.does_policy_exist.response.result.entry.description.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.description.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.description.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.#text | string |  |   23.34.45.67 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.negate-source.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.group.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.group.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.group.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.#text | string |  |   Phantom URL List for do_not_del 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.disabled.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.disabled.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.disabled.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.disabled.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.tag.member | string |  |   test_tag 
action_result.summary.does_policy_exist.response.result.entry.disabled | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.rule-type | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.description | string |  |   Test playbook policy 
action_result.summary.does_policy_exist.response.result.entry.negate-source | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member | string |  |   Phantom URL List for do_not_del 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-destination | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.application.member | string |  |   3pc 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles | string |  |  
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'unblock application'
Unblock an application

Type: **correct**  
Read only: **False**

This action will remove the application from the Application group that was created/updated in the <b>block application</b> action. If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.<br>Note: This action will pass for any non-existing application name as API doesn't return an error for an incorrect application name.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**application** |  required  | Application to unblock | string |  `network application` 
**device_group** |  required  | Device group in which you want to unblock application | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.application | string |  `network application`  |   1c-enterprise 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.delete_application_from_application_group.response.msg | string |  |   command succeeded 
action_result.summary.delete_application_from_application_group.response.@code | string |  |   20 
action_result.summary.delete_application_from_application_group.response.@status | string |  |   success 
action_result.summary.commit_config.finished_job.id | string |  |   2921 
action_result.summary.commit_config.finished_job.tdeq | string |  |   03:19:06 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/09/26 03:19:06 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/09/26 03:19:31 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.queued | string |  |   NO 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_config.finished_job.stoppable | string |  |   no 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   2932 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   03:19:32 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/09/26 03:19:32 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/09/26 03:19:32 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   NO 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   no 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/09/26 03:20:03 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   FAIL 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit failed 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   03:19:33 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   2933 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   error 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   no 
action_result.message | string |  |   command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'block ip'
Block an IP

Type: **contain**  
Read only: **False**

<p>This action uses a multistep approach to block an IP. The approach differs whether <b>is_source_address</b> is true or not.  By default, it is false.  The procedure is as follows:</p><ul><li>Create an address entry named '<b>[ip_address] Added By Splunk SOAR</b>' with the specified IP address<li>If the option <b>should_add_tag</b> is enabled, the container id of the phantom action is added as a tag to the address entry when it's created<li>If <b>is_source_address</b> is false:<ul><li> add this entry to an address group called <b>Phantom Network List for [device_group]</b></li><li>The address entry and group will be created in the device group specified in the <b>device_group</b> parameter</li><li>If a <b>policy_name</b> is provided, configure the address group as a <i>destination</i> to the policy specified in the <b>policy_name</b> parameter</li></ul>If <b>is_source_address</b> is true:<ul><li>add this entry to an address group called <b>PhantomNtwrkSrcLst[device_group]</b></li><li>The address entry and group will be created in the device group specified in the <b>device_group</b> parameter</li><li>If a <b>policy_name</b> is provided, configure the address group as a <i>source</i> to the policy specified in the <b>policy_name</b> parameter</ul><b>Note:</b> If the policy is not found on the device, the action will return an error.<li>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.</li></ul><p><b>Please Note:</b> If the Panorama Policy that is used to block a source or destination address has 'Any' in the Source Address or Destination Address field, Block IP will succeed but it will not work.  Therefore, make sure that the policy that the address group will be appended to has no 'Any' in the field that you are blocking from.  i.e, if you are blocking an IP from source, make sure the policy does not have 'Any' under Source Address.</p><p>The address group name is limited to 32 characters.  The device group chosen will be appended to the address group name created.  If the resulting name is too long, the name will be trimmed, which may result in clipped or unusual names.  This is as intended, as it is a limitation by Panorama.</p>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to block | string |  `ip` 
**is_source_address** |  optional  | Source address | boolean | 
**device_group** |  required  | Device group in which you want to block ip | string |  `panorama device group` 
**policy_type** |  optional  | Block policy type | string | 
**policy_name** |  optional  | Policy to use | string |  `panorama policy name` 
**audit_comment** |  optional  | Audit comment to be used with the policy name. Maximum 256 characters | string | 
**should_add_tag** |  optional  | Whether a new tag should added as part of adding a new IP address | boolean | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.audit_comment | string |  |   updated description 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.ip | string |  `ip`  |   10.1.1.1 
action_result.parameter.is_source_address | boolean |  |   True 
action_result.parameter.policy_name | string |  `panorama policy name`  |   test_policy 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.should_add_tag | boolean |  |   True  False 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.add_address_entry.link_tag_to_ip.response.msg | string |  |   command succeeded 
action_result.summary.add_address_entry.link_tag_to_ip.response.@code | string |  |   20 
action_result.summary.add_address_entry.link_tag_to_ip.response.@status | string |  |   success 
action_result.summary.add_ip_to_address_group.response.msg | string |  |   command succeeded 
action_result.summary.add_ip_to_address_group.response.@code | string |  |   20 
action_result.summary.add_ip_to_address_group.response.@status | string |  |   success 
action_result.summary.add_address_entry.add_tag.response.msg | string |  |   command succeeded 
action_result.summary.add_address_entry.add_tag.response.@code | string |  |   20 
action_result.summary.add_address_entry.add_tag.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.@code | string |  |   19 
action_result.summary.does_policy_exist.response.result.entry.to.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.@loc | string |  |   dg1 
action_result.summary.does_policy_exist.response.result.entry.from.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.@name | string |  |   DO_NOT_DELETE 
action_result.summary.does_policy_exist.response.result.entry.@time | string |  |   2023/09/26 00:16:55 
action_result.summary.does_policy_exist.response.result.entry.@uuid | string |  |   6c809822-a080-46f6-b28e-e1dd5150719c 
action_result.summary.does_policy_exist.response.result.entry.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.source.@time | string |  |   2023/09/26 00:08:51 
action_result.summary.does_policy_exist.response.result.entry.source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.@dirtyId | string |  |   484 
action_result.summary.does_policy_exist.response.result.entry.target.negate | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.service.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.@dirtyId | string |  |   508 
action_result.summary.does_policy_exist.response.result.entry.category.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.group-tag | string |  |   do_not_delete_tag 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.application.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.description | string |  |   Test 
action_result.summary.does_policy_exist.response.result.entry.destination.@time | string |  |   2023/09/26 00:16:55 
action_result.summary.does_policy_exist.response.result.entry.destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.@dirtyId | string |  |   508 
action_result.summary.does_policy_exist.response.result.entry.source-user.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.@count | string |  |   1 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   1 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.update_security_policy.response.msg | string |  |   command succeeded 
action_result.summary.update_security_policy.response.@code | string |  |   20 
action_result.summary.update_security_policy.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result.entry.to.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.to.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.to.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.to.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.to.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.tag.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.#text | string |  |   test_tag 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.from.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.from.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.from.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.from.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.action.#text | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.action.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.action.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source.member.#text | string |  |   12.23.34.45 
action_result.summary.does_policy_exist.response.result.entry.source.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.service.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.service.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.service.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.service.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.service.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.category.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.category.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.category.member.#text | string |  |   auctions 
action_result.summary.does_policy_exist.response.result.entry.category.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.category.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.category.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.category.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.rule-type.#text | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.application.@time | string |  |   2023/10/03 23:44:32 
action_result.summary.does_policy_exist.response.result.entry.application.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.#text | string |  |   3pc 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.application.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.description.#text | string |  |   Test playbook policy 
action_result.summary.does_policy_exist.response.result.entry.description.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.description.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.description.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination.member.#text | string |  |   23.34.45.67 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.#text | string |  |   Phantom URL List for do_not_del 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@time | string |  |   2023/10/03 23:44:35 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.profile-setting.profiles.url-filtering.@dirtyId | string |  |   6 
action_result.summary.update_audit_comment.response.result | string |  |   Successfully added comment for xpath 
action_result.summary.update_audit_comment.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.#text | string |  |   23.34.45.67 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.#text | string |  |   12.23.34.45 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@time | string |  |   2023/10/03 23:44:31 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.negate-source.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.negate-source.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@time | string |  |   2023/10/04 00:05:40 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.negate-destination.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.disabled.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.disabled.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.disabled.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.disabled.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.#text | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@time | string |  |   2023/10/04 01:26:35 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable.@dirtyId | string |  |   10 
action_result.summary.does_policy_exist.response.result.entry.tag.member | string |  |   test_tag 
action_result.summary.does_policy_exist.response.result.entry.source.member | string |  |   12.23.34.45 
action_result.summary.does_policy_exist.response.result.entry.disabled | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.rule-type | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.destination.member | string |  |   23.34.45.67 
action_result.summary.does_policy_exist.response.result.entry.negate-source | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.icmp-unreachable | string |  |   no 
action_result.summary.does_policy_exist.response.result.entry.negate-destination | string |  |   no 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'unblock ip'
Unblock an IP

Type: **correct**  
Read only: **False**

This action will remove the address entry from the Address group that was created/updated in the <b>block ip</b> action.  This action behaves differently based upon whether <b>is_source_address</b> is true or false.  By default, it is false.<br>If <b>is_source_address</b> is false:<ul><li>The given IP address will be removed from the <b>Phantom Network List for [device_group]</b> Address Group.</li></ul>If <b>is_source_address</b> is true:<ul><li>The given IP address will be removed from the <b>PhantomNtwrkSrcLst[device_group]</b> Address Group.</li></ul>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to unblock | string |  `ip` 
**is_source_address** |  optional  | Source address | boolean | 
**device_group** |  required  | Device group in which you want to unblock ip | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.ip | string |  `ip`  |   10.1.1.1 
action_result.parameter.is_source_address | boolean |  |   True 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.delete_ip_from_address_group.response.msg | string |  |   command succeeded 
action_result.summary.delete_ip_from_address_group.response.@code | string |  |   20 
action_result.summary.delete_ip_from_address_group.response.@status | string |  |   success 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list applications'
List the applications that the device knows about and can block

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.data.\*.@id | string |  |  
action_result.data.\*.@minver | string |  |  
action_result.data.\*.@name | string |  `network application`  |  
action_result.data.\*.@ori_country | string |  |  
action_result.data.\*.@ori_lauguage | string |  |  
action_result.data.\*.able-to-transfer-file | string |  |  
action_result.data.\*.alg-disable-capability | string |  |  
action_result.data.\*.analysis | string |  |  
action_result.data.\*.application-container | string |  |  
action_result.data.\*.breaks-decryption | string |  |  
action_result.data.\*.category | string |  |  
action_result.data.\*.child | string |  |  
action_result.data.\*.consume-big-bandwidth | string |  |  
action_result.data.\*.correlate.interval | string |  |  
action_result.data.\*.correlate.key-by.member | string |  |  
action_result.data.\*.correlate.rule-match | string |  |  
action_result.data.\*.correlate.rules.entry.interval | string |  |  
action_result.data.\*.correlate.rules.entry.protocol | string |  |  
action_result.data.\*.correlate.rules.entry.threshold | string |  |  
action_result.data.\*.correlate.rules.entry.track-by.member | string |  |  
action_result.data.\*.data-ident | string |  |  
action_result.data.\*.decode | string |  |  
action_result.data.\*.decode.#text | string |  |  
action_result.data.\*.decode.@minver | string |  |  
action_result.data.\*.default.\*.ident-by-ip-protocol | string |  |  
action_result.data.\*.default.\*.port.member | string |  |  
action_result.data.\*.default.ident-by-icmp-type | string |  |  
action_result.data.\*.default.ident-by-ip-protocol | string |  |  
action_result.data.\*.default.port.member | string |  |  
action_result.data.\*.default.port.member | string |  |  
action_result.data.\*.deprecated | string |  |  
action_result.data.\*.description | string |  |  
action_result.data.\*.discard-timeout | string |  |  
action_result.data.\*.doc-review | string |  |  
action_result.data.\*.enable-url-filter | string |  |  
action_result.data.\*.evasive-behavior | string |  |  
action_result.data.\*.file-forward | string |  |  
action_result.data.\*.file-forward | string |  |  
action_result.data.\*.file-type-ident | string |  |  
action_result.data.\*.ha-safe | string |  |  
action_result.data.\*.has-known-vulnerability | string |  |  
action_result.data.\*.ident-by-dport | string |  |  
action_result.data.\*.ident-by-sport | string |  |  
action_result.data.\*.implicit-use-applications.member | string |  |  
action_result.data.\*.implicit-use-applications.member | string |  |  
action_result.data.\*.netx-vmotion | string |  |  
action_result.data.\*.not-support-ssl | string |  |  
action_result.data.\*.ottawa-name | string |  |  
action_result.data.\*.pervasive-use | string |  |  
action_result.data.\*.preemptive | string |  |  
action_result.data.\*.prone-to-misuse | string |  |  
action_result.data.\*.references.entry.\*.@name | string |  |  
action_result.data.\*.references.entry.\*.link | string |  |  
action_result.data.\*.references.entry.@name | string |  |  
action_result.data.\*.references.entry.link | string |  |  
action_result.data.\*.related-applications.member | string |  |  
action_result.data.\*.risk | string |  |  
action_result.data.\*.risk | string |  |  
action_result.data.\*.subcategory | string |  |  
action_result.data.\*.tcp-discard-timeout | string |  |  
action_result.data.\*.tcp-timeout | string |  |  
action_result.data.\*.technology | string |  |  
action_result.data.\*.timeout | string |  |  
action_result.data.\*.timeout | string |  |  
action_result.data.\*.tunnel-applications.@minver | string |  |  
action_result.data.\*.tunnel-applications.member | string |  |  
action_result.data.\*.tunnel-applications.member | string |  |  
action_result.data.\*.tunnel-applications.member.#text | string |  |  
action_result.data.\*.tunnel-applications.member.\*.#text | string |  |  
action_result.data.\*.tunnel-applications.member.\*.@minver | string |  |  
action_result.data.\*.tunnel-applications.member.@minver | string |  |  
action_result.data.\*.tunnel-other-application | string |  |  
action_result.data.\*.tunnel-other-application.#text | string |  |  
action_result.data.\*.tunnel-other-application.@minver | string |  |  
action_result.data.\*.udp-discard-timeout | string |  |  
action_result.data.\*.udp-timeout | string |  |  
action_result.data.\*.use-applications.\*.member | string |  |  
action_result.data.\*.use-applications.@minver | string |  |  
action_result.data.\*.use-applications.member | string |  |  
action_result.data.\*.use-applications.member | string |  |  
action_result.data.\*.use-applications.member.#text | string |  |  
action_result.data.\*.use-applications.member.\*.#text | string |  |  
action_result.data.\*.use-applications.member.\*.@minver | string |  |  
action_result.data.\*.use-applications.member.@minver | string |  |  
action_result.data.\*.used-by-malware | string |  |  
action_result.data.\*.virus-ident | string |  |  
action_result.summary.total_applications | numeric |  |   1 
action_result.message | string |  |   Total applications: 2421 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'run query'
Run a query on Panorama

Type: **investigate**  
Read only: **True**

This action runs a query on Panorama and returns the set of logs matching the search criteria.<br><br>Use the <b>range</b> parameter to limit the number of logs returned by the action. If no range is given, the action will use the range <b>1-5000</b>. The action can retrieve up to a maximum of 5000 logs. If more logs need to be retrieved, rerun the action with the next sequential range of values.<br><br>The <b>log_type</b> parameter can be one of the following:<ul><li><b>traffic</b> - traffic logs</li><li><b>url</b> - URL filtering logs</li><li><b>data</b> - data filtering logs</li><li><b>threat</b> - threat logs</li><li><b>config</b> - config logs</li><li><b>system</b> - system logs</li><li><b>hipmatch</b> - HIP match logs</li><li><b>wildfire</b> - wildfire logs</li><li><b>corr</b> - correlated event logs</li><li><b>corr-categ</b> - correlated events by category</li><li><b>corr-detail</b> - correlated event details.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**log_type** |  required  | Log type to query | string | 
**query** |  required  | Query to run | string | 
**range** |  optional  | Range of result logs to retrieve (e.g 1-5000 or 100-700) | string | 
**direction** |  optional  | Direction to search | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.direction | string |  |   backward 
action_result.parameter.log_type | string |  |   traffic 
action_result.parameter.query | string |  |   ( port.dst eq 161 ) 
action_result.parameter.range | string |  |   1-5000 
action_result.data.\*.job.cached-logs | string |  |   21 
action_result.data.\*.job.id | string |  |   1316 
action_result.data.\*.job.status | string |  |   FIN 
action_result.data.\*.job.tdeq | string |  |   15:46:37 
action_result.data.\*.job.tenq | string |  |   15:46:37 
action_result.data.\*.job.tlast | string |  |   16:00:00 
action_result.data.\*.log.logs.@count | string |  |   21 
action_result.data.\*.log.logs.@progress | string |  |   1 
action_result.data.\*.log.logs.entry.\*.@logid | string |  |   7592 
action_result.data.\*.log.logs.entry.\*.action | string |  |   allow 
action_result.data.\*.log.logs.entry.\*.action_source | string |  |   from-policy 
action_result.data.\*.log.logs.entry.\*.actionflags | string |  |   0x8000000000000000 
action_result.data.\*.log.logs.entry.\*.app | string |  |   snmp-base 
action_result.data.\*.log.logs.entry.\*.bytes | string |  |   79 
action_result.data.\*.log.logs.entry.\*.bytes_received | string |  |   0 
action_result.data.\*.log.logs.entry.\*.bytes_sent | string |  |   79 
action_result.data.\*.log.logs.entry.\*.captive-portal | string |  |   No 
action_result.data.\*.log.logs.entry.\*.category | string |  |   any 
action_result.data.\*.log.logs.entry.\*.config_ver | string |  |   1 
action_result.data.\*.log.logs.entry.\*.cpadding | string |  |   0 
action_result.data.\*.log.logs.entry.\*.decrypt-mirror | string |  |   No 
action_result.data.\*.log.logs.entry.\*.device_name | string |  |   PA-VM 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_1 | string |  |   17 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_2 | string |  |   0 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_3 | string |  |   0 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_4 | string |  |   0 
action_result.data.\*.log.logs.entry.\*.domain | string |  `domain`  |   1 
action_result.data.\*.log.logs.entry.\*.dport | string |  `port`  |   161 
action_result.data.\*.log.logs.entry.\*.dst | string |  `ip`  |   10.18.3.2 
action_result.data.\*.log.logs.entry.\*.dstloc | string |  |   10.0.0.0-10.255.255.255 
action_result.data.\*.log.logs.entry.\*.elapsed | string |  |   0 
action_result.data.\*.log.logs.entry.\*.flag-flagged | string |  |   No 
action_result.data.\*.log.logs.entry.\*.flag-nat | string |  |   No 
action_result.data.\*.log.logs.entry.\*.flag-pcap | string |  |   No 
action_result.data.\*.log.logs.entry.\*.flag-proxy | string |  |   No 
action_result.data.\*.log.logs.entry.\*.flag-url-denied | string |  |   No 
action_result.data.\*.log.logs.entry.\*.flags | string |  |   0x64 
action_result.data.\*.log.logs.entry.\*.from | string |  |   Internal Zone 
action_result.data.\*.log.logs.entry.\*.inbound_if | string |  |   ethernet1/1 
action_result.data.\*.log.logs.entry.\*.logset | string |  |   Forward all logs from DG2 
action_result.data.\*.log.logs.entry.\*.natdport | string |  |   0 
action_result.data.\*.log.logs.entry.\*.natsport | string |  |   0 
action_result.data.\*.log.logs.entry.\*.non-std-dport | string |  |   No 
action_result.data.\*.log.logs.entry.\*.outbound_if | string |  |   ethernet1/1 
action_result.data.\*.log.logs.entry.\*.packets | string |  |   1 
action_result.data.\*.log.logs.entry.\*.padding | string |  |   0 
action_result.data.\*.log.logs.entry.\*.pbf-c2s | string |  |   No 
action_result.data.\*.log.logs.entry.\*.pbf-s2c | string |  |   No 
action_result.data.\*.log.logs.entry.\*.pkts_received | string |  |   0 
action_result.data.\*.log.logs.entry.\*.pkts_sent | string |  |   1 
action_result.data.\*.log.logs.entry.\*.proto | string |  |   udp 
action_result.data.\*.log.logs.entry.\*.receive_time | string |  |   2017/06/23 15:35:54 
action_result.data.\*.log.logs.entry.\*.repeatcnt | string |  |   1 
action_result.data.\*.log.logs.entry.\*.rule | string |  |   Test URL Security Policy 
action_result.data.\*.log.logs.entry.\*.seqno | string |  |   1715 
action_result.data.\*.log.logs.entry.\*.serial | string |  |   007200000031753 
action_result.data.\*.log.logs.entry.\*.session_end_reason | string |  |   aged-out 
action_result.data.\*.log.logs.entry.\*.sessionid | string |  |   58 
action_result.data.\*.log.logs.entry.\*.sport | string |  `port`  |   64453 
action_result.data.\*.log.logs.entry.\*.src | string |  `ip`  |   10.10.0.18 
action_result.data.\*.log.logs.entry.\*.srcloc | string |  |   10.0.0.0-10.255.255.255 
action_result.data.\*.log.logs.entry.\*.start | string |  |   2017/06/23 15:35:21 
action_result.data.\*.log.logs.entry.\*.subtype | string |  |   end 
action_result.data.\*.log.logs.entry.\*.sym-return | string |  |   No 
action_result.data.\*.log.logs.entry.\*.temporary-match | string |  |   No 
action_result.data.\*.log.logs.entry.\*.time_generated | string |  |   2017/06/23 15:35:50 
action_result.data.\*.log.logs.entry.\*.time_received | string |  |   2017/06/23 15:35:50 
action_result.data.\*.log.logs.entry.\*.to | string |  |   Internal Zone 
action_result.data.\*.log.logs.entry.\*.transaction | string |  |   No 
action_result.data.\*.log.logs.entry.\*.type | string |  |   TRAFFIC 
action_result.data.\*.log.logs.entry.\*.vsys | string |  |   vsys1 
action_result.data.\*.log.logs.entry.\*.vsys_id | string |  |   1 
action_result.summary.num_logs | numeric |  |   21 
action_result.summary.run_query.response.@code | string |  |   19 
action_result.summary.run_query.response.result.job | string |  |   852 
action_result.summary.run_query.response.result.msg.line | string |  |   query job enqueued with jobid 852 
action_result.summary.run_query.response.@status | string |  |   success 
action_result.summary.finished_job.id | string |  |   852 
action_result.summary.finished_job.tdeq | string |  |   04:32:51 
action_result.summary.finished_job.tenq | string |  |   04:32:51 
action_result.summary.finished_job.tlast | string |  |   16:00:00 
action_result.summary.finished_job.status | string |  |   FIN 
action_result.summary.finished_job.cached-logs | string |  |   0 
action_result.message | string |  |   Num logs: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'commit changes'
Commit changes to the firewall and device groups

Type: **generic**  
Read only: **False**

The action proceeds to commit the changes to Panorama, followed by a commit to the device group. If the device group happens to be shared, then a commit will be sent to all the device groups belonging to it. Regardless of the value provided in device group parameter, pending changes of all the device groups will be committed and the action will then proceed with pushing the changes to the firewall (if linked to that device group) of mentioned device group.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**device_group** |  required  | Device group whose changes you want to push to firewall | string |  `panorama device group` 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_group 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.commit_config.finished_job.id | string |  |   2834 
action_result.summary.commit_config.finished_job.tdeq | string |  |   02:22:04 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/09/26 02:22:04 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/09/26 02:22:30 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.queued | string |  |   NO 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_config.finished_job.stoppable | string |  |   no 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   2845 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   02:22:31 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/09/26 02:22:31 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/09/26 02:22:31 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   test 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   NO 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   no 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/10/17 22:32:21 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit succeeded 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   22:31:33 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   3970 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   success 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn.entry.\*.#text | string |  |   { "uuid" : "8ec4cbb8-4ab9-4ae3-8a9f-7cb3d9b3324a", "serial" : "007951000393837", "rulename" : "test_91", "ruletype" : "security", "vsys" : [{ "id" : "vsys1", "dgid" : 43, "shadowed-rule" : [ "Allow Panorama Comm", "General Blocked Sites", "LAN to WAN internet Access", "Social Media Block", "cp_1", "cp_2", "create_policy", "create_policy_1", "create_policy_2", "create_policy_3", "create_policy_4", "create_policy_4fe", "create_policy_4fed", "test_test_policy", "test2    .-_", "test1 test", "part_5", "test", "test12345", "test_123_policy", "test_create_policy", "test_pol_12", "test_policy_123", "test_post_rule_shared", "example"]}]} 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn.entry.\*.@name | string |  |   8ec4cbb8-4ab9-4ae3-8a9f-7cb3d9b3324a 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   no 
action_result.message | string |  |   command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get threat pcap'
Export a Threat PCAP file

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**pcap_id** |  required  | PCAP ID required to fetch Threat PCAP | string |  `panorama pcap id` 
**device_name** |  required  | Device Name required to fetch Threat PCAP | string |  `panorama device name` 
**session_id** |  required  | Session ID required to fetch Threat PCAP | string |  `panorama session id` 
**search_time** |  required  | Search time that the Threat PCAP was received on the firewall (yyyy/mm/dd hr:min:sec) | string |  `timestamp` 
**filename** |  optional  | Filename of exported PCAP file | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_name | string |  `panorama device name`  |  
action_result.parameter.filename | string |  |  
action_result.parameter.pcap_id | string |  `panorama pcap id`  |  
action_result.parameter.search_time | string |  `timestamp`  |  
action_result.parameter.session_id | string |  `panorama session id`  |  
action_result.data.\*.vault_id | string |  |   testff855c129457453de6a5cde58d19add6fbe31 
action_result.data.\*.file_name | string |  |   test.pcap 
action_result.summary.message | string |  |   PCAP file added successfully to the vault 
action_result.message | string |  |   Message: PCAP file added successfully to the vault 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list edl'
List External Dynamic Lists

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**device_group** |  required  | Device group whose edl you want to list (up to 31 characters, default is 'shared') | string |  `panorama device group` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   dg5 
action_result.data.\*.@admin | string |  |   admin 
action_result.data.\*.@dirtyId | string |  |   59 
action_result.data.\*.@name | string |  `panorama edl name`  |  
action_result.data.\*.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.disable-override.#text | string |  |   Yes 
action_result.data.\*.disable-override.@admin | string |  |   admin 
action_result.data.\*.disable-override.@dirtyId | string |  |   59 
action_result.data.\*.disable-override.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.@admin | string |  |   admin 
action_result.data.\*.type.@dirtyId | string |  |   59 
action_result.data.\*.type.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.ip.@admin | string |  |   admin 
action_result.data.\*.type.ip.@dirtyId | string |  |   59 
action_result.data.\*.type.ip.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.ip.recurring.@admin | string |  |   admin 
action_result.data.\*.type.ip.recurring.@dirtyId | string |  |   59 
action_result.data.\*.type.ip.recurring.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.ip.recurring.monthly.@admin | string |  |   admin 
action_result.data.\*.type.ip.recurring.monthly.@dirtyId | string |  |   59 
action_result.data.\*.type.ip.recurring.monthly.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.ip.recurring.monthly.at.#text | string |  |   07 
action_result.data.\*.type.ip.recurring.monthly.at.@admin | string |  |   admin 
action_result.data.\*.type.ip.recurring.monthly.at.@dirtyId | string |  |   59 
action_result.data.\*.type.ip.recurring.monthly.at.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.ip.recurring.monthly.day-of-month.#text | string |  |   12 
action_result.data.\*.type.ip.recurring.monthly.day-of-month.@admin | string |  |   admin 
action_result.data.\*.type.ip.recurring.monthly.day-of-month.@dirtyId | string |  |   59 
action_result.data.\*.type.ip.recurring.monthly.day-of-month.@time | string |  |   2023/10/15 03:16:57 
action_result.data.\*.type.ip.url.#text | string |  |   http://www.test.com 
action_result.data.\*.type.ip.url.@admin | string |  |   admin 
action_result.data.\*.type.ip.url.@dirtyId | string |  |   59 
action_result.data.\*.type.ip.url.@time | string |  |   2023/10/15 03:16:57 
action_result.summary | string |  |  
action_result.summary.total_external_dynamic_lists | numeric |  |   1 
action_result.message | string |  |   Total external dynamic lists: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get edl'
Get data of an External Dynamic List

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of the external dynamic list you want to get data off (up to 63 characters) | string |  `panorama edl name` 
**device_group** |  required  | Device group in which the edl exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   dg1 
action_result.parameter.name | string |  `panorama edl name`  |   edl_name 
action_result.data.\*.@loc | string |  |   dg1 
action_result.data.\*.@name | string |  |   test edl 1 
action_result.data.\*.disable-override | string |  |   No 
action_result.data.\*.type.ip.certificate-profile | string |  |   test123 
action_result.data.\*.type.ip.description | string |  |   This is test edl description 
action_result.data.\*.type.ip.recurring.monthly.at | string |  |   10 
action_result.data.\*.type.ip.recurring.monthly.day-of-month | string |  |   22 
action_result.data.\*.type.ip.url | string |  |   www.test.com 
action_result.summary | string |  |  
action_result.message | string |  |   Successfully fetched EDL details 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'create edl'
Create an External Dynamic List

Type: **contain**  
Read only: **False**

<h4>Action Keynote</h4><ul><li>If the <b>device_group</b> doesn't exist, it will create a new <b>device_group</b>.</li><li>The certificate profile you select must have root CA (certificate authority) and intermediate CA certificates that match the certificates installed on the server you are authenticating.</li><li>The default value for <b>hour</b> is '0'.</li><li>The default value for <b>day_of_week</b> is 'Sunday'.</li><li>Exception list is used to exclude entries from an external dynamic list and gives you the option to enforce policy on some (but not all) of the entries in a list. exception list have an IP address, domain, or URL(depending on the type of list).</li><li>Exception list can have at max 100 exception values.</li><li>If the list type is <b>Subscriber Identity List(IMSI)</b>, in the exception list IMSI prefix can have 6 digit values followed by '\*'.<ul><li><code>Example : '123456\*'</code>.</li></ul></li><li>If the list type is <b>Equipment Identity List(IMEI)</b>, in the exception list IMSI prefix can have 8 digit values followed by '\*'.<ul><li><code>Example : '12345678\*'</code>.</li></ul></li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of the external dynamic list you want to create (up to 63 characters) | string |  `panorama edl name` 
**device_group** |  required  | Device group in which you want to create the edl (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**description** |  optional  | Description of external dynamic list (max char : 255) | string | 
**list_type** |  required  | Type of external dynamic list | string | 
**source** |  required  | Source url to fetch the data | string | 
**exception_list** |  optional  | List of exceptions (comma separated values) | string | 
**expand_for_subdomains** |  optional  | Expand to include subdomains of a specified domain automatically (only used when list_type is Domain list) | string | 
**disable_override** |  optional  | Used to ensure that a firewall administrator cannot override settings locally on a firewall that inherits this configuration through a Device Group commit from Panorama (only used when device group is not 'shared') | string | 
**certificate_profile** |  optional  | Certificate profile is used for authenticating the server that hosts the list (only used when list_type is not predefined IP or URL) | string | 
**check_for_updates** |  optional  | Defines the frequency at which the firewall retrieves the list  (only used when list_type is not predefined IP or URL) | string | 
**hour** |  optional  | At what hour of the day to check for updates  (only used when check_for_update type is daily, weekly or monthly) | string | 
**day_of_week** |  optional  | On which specific day of week to check for updates (only used when check_for_update type is weekly) | string | 
**day_of_month** |  optional  | On which specific date of month to check for updates (only used when check_for_update type is monthly) | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.certificate_profile | string |  |   None 
action_result.parameter.check_for_updates | string |  |   Hourly 
action_result.parameter.day_of_month | string |  |   22 
action_result.parameter.day_of_week | string |  |   Sunday 
action_result.parameter.description | string |  |   Test description for edl 
action_result.parameter.device_group | string |  `panorama device group`  |   dg5 
action_result.parameter.disable_override | string |  |   Yes  No 
action_result.parameter.exception_list | string |  |   test1.com, test2.com 
action_result.parameter.expand_for_subdomains | string |  |   Yes  No 
action_result.parameter.hour | string |  |   12 
action_result.parameter.list_type | string |  |   IP List 
action_result.parameter.name | string |  `panorama edl name`  |   edl_name 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.source | string |  |   http://test.com 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data.\*.@count | string |  |   0 
action_result.data.\*.@total-count | string |  |   0 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.id | string |  |   3639 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   03:14:30 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/10/15 03:14:30 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/10/15 03:14:56 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   3650 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   03:15:00 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/10/15 03:15:00 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/10/15 03:15:00 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.create_edl.response.@code | string |  |   20 
action_result.summary.create_edl.response.@status | string |  |   success 
action_result.summary.create_edl.response.msg | string |  |   command succeeded 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'modify edl'
Modify an External Dynamic List

Type: **generic**  
Read only: **False**

<h4>Action Keynote</h4><ul><li>This action is used to modify the existing edl data. The parameters for which data is provided will only be updated.</li><li>The certificate profile you select must have root CA (certificate authority) and intermediate CA certificates that match the certificates installed on the server you are authenticating.</li><li>Exception list is used to exclude entries from an external dynamic list and gives you the option to enforce policy on some (but not all) of the entries in a list. exception list have an IP address, domain, or URL(depending on the type of list). </li><li>Exception list can have at max 100 exception values.</li><li>If the list type is <b>Subscriber Identity List(IMSI)</b>, in the exception list IMSI prefix can have 6 digit values followed by '\*'.<ul><li><code>Example : '123456\*'</code>.</li></ul></li><li>If the list type is <b>Equipment Identity List(IMEI)</b>, in the exception list IMSI prefix can have 8 digit values followed by '\*'.<ul><li><code>Example : '12345678\*'</code>.</li></ul></li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of the external dynamic list you want to modify (up to 63 characters) | string |  `panorama edl name` 
**device_group** |  required  | Device group in which the edl exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**description** |  optional  | Description of external dynamic list (max char : 255) | string | 
**list_type** |  optional  | Type of external dynamic list | string | 
**source** |  optional  | Source url to fetch the data | string | 
**exception_list** |  optional  | List of exceptions (comma separated values) | string | 
**expand_for_subdomains** |  optional  | Expand to include subdomains of a specified domain automatically (only used when list_type is Domain list) | string | 
**disable_override** |  optional  | Used to ensure that a firewall administrator cannot override settings locally on a firewall that inherits this configuration through a Device Group commit from Panorama (only used when device group is not 'shared') | string | 
**certificate_profile** |  optional  | Certificate profile is used for authenticating the server that hosts the list (only used when list_type is not predefined IP or URL) | string | 
**check_for_updates** |  optional  | Defines the frequency at which the firewall retrieves the list  (only used when list_type is not predefined IP or URL) | string | 
**hour** |  optional  | At what hour of the day to check for updates (only used when check_for_update type is daily, weekly or monthly) | string | 
**day_of_week** |  optional  | On which specific day of week to check for updates (only used when check_for_update type is weekly) | string | 
**day_of_month** |  optional  | On which specific date of month to check for updates (only used when check_for_update type is monthly) | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.certificate_profile | string |  |   None 
action_result.parameter.check_for_updates | string |  |   Hourly 
action_result.parameter.day_of_month | string |  |   1 
action_result.parameter.day_of_week | string |  |   Sunday 
action_result.parameter.description | string |  |   Test description for edl 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.parameter.disable_override | string |  |   Yes  No 
action_result.parameter.exception_list | string |  |   test.com 
action_result.parameter.expand_for_subdomains | string |  |   Yes  No 
action_result.parameter.hour | string |  |   10 
action_result.parameter.list_type | string |  |   IP List 
action_result.parameter.name | string |  `panorama edl name`  |   edl_name 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.source | string |  |   http://test.com 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.id | string |  |   3879 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   02:47:03 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/10/17 02:47:03 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/10/17 02:47:30 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   3890 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   02:47:33 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/10/17 02:47:33 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/10/17 02:47:33 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.modify_edl.response.@code | string |  |   20 
action_result.summary.modify_edl.response.@status | string |  |   success 
action_result.summary.modify_edl.response.msg | string |  |   command succeeded 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'delete edl'
Delete an External Dynamic List

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of the external dynamic list you want to delete (up to 63 characters) | string |  `panorama edl name` 
**device_group** |  required  | Device group in which the edl exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   device_group 
action_result.parameter.name | string |  `panorama edl name`  |   edl_name 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.id | string |  |   3651 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   03:19:54 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/10/15 03:19:54 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/10/15 03:20:20 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   3662 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   03:20:21 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/10/15 03:20:21 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/10/15 03:20:21 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.delete_edl.response.@code | string |  |   20 
action_result.summary.delete_edl.response.@status | string |  |   success 
action_result.summary.delete_edl.response.msg | string |  |   command succeeded 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'create policy'
Create a security policy rule

Type: **contain**  
Read only: **False**

<p><h4>Action Keynote</h4><ul><li>For source and destination address parameters, to add a region, provide only the abbreviation of region. That is for region US (United States) enter US as input.</li><li>When rule_type parameter is 'interzone' the destination zone parameter will be ignored.</li></ul></p>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**policy_name** |  required  | Name of the security policy rule (max length is 63 characters, which can be letters, numbers, spaces, hyphens, dot and underscores) | string |  `panorama policy name` 
**device_group** |  required  | Device group to create the policy rule in (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**policy_type** |  required  | Rule base to create the policy in (pre-rule or post-rule) | string | 
**rule_type** |  required  | Rule type of the policy rule (specifies whether the rule applies to traffic within a zone, between zones, or both) | string | 
**description** |  optional  | Description for the policy (max length 1024 characters) | string | 
**tag** |  optional  | List of tags(comma separated) to apply to this policy (allow to group objects using keywords or phrases, max length 127 characters) | string | 
**audit_comment** |  optional  | Describe the changes made and why the rule was created by adding an audit comment(once the configuration is commited, it would be reflected in Audit Comment Archive for future reference) | string | 
**source_zone** |  required  | Source zones for policy (default is Any) | string | 
**source_address** |  required  | List of source addresses, address groups, or regions (comma separated, default is Any) to be added to the policy | string | 
**negate_source** |  optional  | Whether to negate the source (apply the rule to source addresses from the specified zone except for the addresses specified) | string | 
**source_user** |  optional  | List of source users or groups of users (comma separated) subject to the policy | string | 
**source_device** |  optional  | List of host devices(comma separated) subject to the policy | string | 
**destination_zone** |  required  | Destinations zones(comma separated) for policy (default is Any) | string | 
**destination_device** |  optional  | List of host devices(comma separated) subject to the policy | string | 
**destination_address** |  required  | List of destination addresses, address groups, or regions (comma separated, default is Any) to be added to the policy | string | 
**negate_destination** |  optional  | Whether to negate the destination (apply the rule to destination addresses from the specified zone except for the addresses specified) | string | 
**application** |  required  | List of specific applications(comma separated) for the security policy rule | string | 
**service** |  required  | List of services(comma separated) of the policy (services to limit to specific TCP or UDP port numbers) | string | 
**category** |  optional  | List of URL Categories(comma separated) of the policy | string | 
**profile_setting** |  optional  | Type of profile setting to choose for the policy (additional checking that the firewall performs on packets that match the Security profile rule) | string | 
**action** |  required  | Action the firewall takes on traffic that matches the attributes defined in a rule | string | 
**icmp_unreachable** |  optional  | Whether to send information to the client that a session is not allowed. Applicable only in case action is 'Drop', 'Reset Client', 'Reset Server', 'Reset Both' | string | 
**log_forwarding** |  optional  | To forward the local traffic log and threat log entries to remote destinations, such as Panorama | string | 
**target** |  optional  | Apply the rule to specific firewalls or descendant device groups of the Device Group (or Shared location) where the rule is defined (Takes serial number of firewall as input) | string | 
**where** |  optional  | Where to position the policy, by default the policy would be created at the bottom | string | 
**dst** |  optional  | Policy in reference to which, position the current policy (only applicable when input for 'where' is 'after' or 'before') | string | 
**disable** |  optional  | Whether to disable the policy | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.action | string |  |   allow 
action_result.parameter.application | string |  |   1c-enterprise 
action_result.parameter.audit_comment | string |  |   updated description 
action_result.parameter.category | string |  |   Test URL Category 
action_result.parameter.description | string |  |   Policy rule to deny traffic from a specific address group 
action_result.parameter.destination_address | string |  |   dev_env_address_1  10.1.192.168 
action_result.parameter.destination_device | string |  |   test_device 
action_result.parameter.destination_zone | string |  |   IN 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.disable | string |  |   Yes 
action_result.parameter.dst | string |  |   test_policy_rule_1 
action_result.parameter.icmp_unreachable | string |  |   Yes 
action_result.parameter.log_forwarding | string |  |   IoT Security Default Profile 
action_result.parameter.negate_destination | string |  |   Yes 
action_result.parameter.negate_source | string |  |   Yes 
action_result.parameter.policy_name | string |  `panorama policy name`  |   policy_rule_1 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.profile_setting | string |  |   profiles 
action_result.parameter.rule_type | string |  |   universal 
action_result.parameter.service | string |  |   service-http 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.source_address | string |  |   dev_env_address_1  10.1.192.168 
action_result.parameter.source_device | string |  |   test_device 
action_result.parameter.source_user | string |  |   test_user 
action_result.parameter.source_zone | string |  |   IN 
action_result.parameter.tag | string |  |   test_tag 
action_result.parameter.target | string |  |   000000000000000 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.where | string |  |   after 
action_result.data.\*.@count | string |  |   0 
action_result.data.\*.@total-count | string |  |   0 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.id | string |  |   432 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   04:54:34 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/08/25 04:54:34 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/08/25 04:54:58 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings | string |  |  
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   169 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   error 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings.line | string |  |   External Dynamic List test_edl_test_ip_list is configured with no certificate profile. Please select a certificate profile for performing server certificate validation 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   FAIL 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit failed 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/09/06 03:15:29 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   03:14:54 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   443 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   04:55:01 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/08/25 04:55:01 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/08/25 04:55:01 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.create a policy rule.response.@code | string |  |   20 
action_result.summary.create a policy rule.response.@status | string |  |   success 
action_result.summary.create a policy rule.response.msg | string |  |   command succeeded 
action_result.summary.does_policy_exist.response.@code | string |  |   7 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result | string |  |  
action_result.summary.does_policy_exist.response.result.@count | string |  |   0 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   0 
action_result.summary.update_audit_comment.response.@status | string |  |   success 
action_result.summary.update_audit_comment.response.result | string |  |   Successfully added comment for xpath 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'custom block policy'
Block IP addresses, Address Groups, EDLs(External Dynamic List), Applications, or URL Categories in Panorama and creates a custom uni-directional (direction parameter value as from or to) or bi-directional (direction parameter value as both) security rule

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**policy_name** |  required  | Name of the security policy rule (max length is 63 characters, which can be letters, numbers, spaces, hyphens, dot and underscores) | string |  `panorama policy name` 
**device_group** |  required  | Device group to create the policy rule in (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**policy_type** |  required  | Rule base to create the policy in (pre-rule or post-rule) | string | 
**rule_type** |  required  | Rule type of the policy rule (specifies whether the rule applies to traffic within a zone, between zones, or both) | string | 
**description** |  optional  | Description for the policy (max length 1024 characters) | string | 
**tag** |  optional  | List of tags to apply to this policy (allow to group objects using keywords or phrases, max length 127 characters) | string | 
**audit_comment** |  optional  | Describe the changes made and why the rule was created by adding an audit comment(once the configuration is commited, it would be reflected in Audit Comment Archive for future reference) | string | 
**direction** |  optional  | Direction to block the traffic (Default is 'both') | string | 
**object_type** |  required  | Type of object to block | string | 
**object_value** |  required  | Value of the object to be blocked. Can be a list(comma separated) | string | 
**icmp_unreachable** |  optional  | Whether to send information to the client that a session is not allowed. Applicable only in case action is 'Drop', 'Reset Client', 'Reset Server', 'Reset Both' | string | 
**log_forwarding** |  optional  | To forward the local traffic log and threat log entries to remote destinations, such as Panorama | string | 
**where** |  optional  | Where to position the policy, by default the policy would be created at the bottom | string | 
**dst** |  optional  | Policy in reference to which, position the current policy | string | 
**target** |  optional  | Apply the rule to specific firewalls or descendant device groups of the Device Group (or Shared location) where the rule is defined (Takes serial number of firewall as input) | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.audit_comment | string |  |   updated description 
action_result.parameter.description | string |  |   Test description 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.direction | string |  |   both 
action_result.parameter.dst | string |  |   test_policy_rule_1 
action_result.parameter.icmp_unreachable | string |  |   Yes 
action_result.parameter.log_forwarding | string |  |   IoT Security Default Profile 
action_result.parameter.object_type | string |  |   ip 
action_result.parameter.object_value | string |  |   test_address_2  10.1.10.20 
action_result.parameter.policy_name | string |  `panorama policy name`  |   policy_rule_1 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.rule_type | string |  |   universal 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.tag | string |  |   test_tag 
action_result.parameter.target | string |  |   000000000000000 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.where | string |  |   after 
action_result.data.\*.@count | string |  |   0 
action_result.data.\*.@total-count | string |  |   0 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.does_policy_exist.response.@code | string |  |   7 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result | string |  |  
action_result.summary.does_policy_exist.response.result.@count | string |  |   0 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   0 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'modify policy'
Modify a security policy rule

Type: **generic**  
Read only: **False**

<p><h4>Action Keynote</h4><ul><li>When rule_type parameter is 'interzone' the destination zone parameter will be ignored.</li><li>The <b>device_group</b> and <b>policy_name</b> parameters cannot be modified.</li><li>For source and destination address parameters, to add a region, provide only the abbreviation of region. That is for region US (United States) enter US as input.</li><li>Source address, source zone, source user, source device, destination address, destination zone, destination device, tag, application, service, category, target parameters would append the values to the already existing values in th policy.</li><li>Log forwarding, profile settings, rule type parameters would be replaced.</li></ul></p>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**policy_name** |  required  | Name of the security policy rule | string |  `panorama policy name` 
**device_group** |  required  | Device group of the policy rule (default is 'shared') | string |  `panorama device group` 
**policy_type** |  required  | Rule base of the policy (pre-rule or post-rule) | string | 
**rule_type** |  optional  | Rule type of the policy rule (specifies whether the rule applies to traffic within a zone, between zones, or both) | string | 
**description** |  optional  | Description for the policy (max length 1024 characters) | string | 
**tag** |  optional  | List of tags(comma separated) to apply to this policy (allow to group objects using keywords or phrases, max length 127 characters) | string | 
**audit_comment** |  optional  | Describe the changes made and why the rule was created by adding an audit comment(once the configuration is commited, it would be reflected in Audit Comment Archive for future reference) | string | 
**source_zone** |  optional  | List of source zones(comma separated) for policy (default is Any) | string | 
**source_address** |  optional  | List of source addresses, address groups, or regions (comma separated, default is Any) to be added to the policy | string | 
**negate_source** |  optional  | Whether to negate the source (apply the rule to source addresses from the specified zone except for the addresses specified) | string | 
**source_user** |  optional  | List of source users or groups of users(comma separated) subject to the policy | string | 
**source_device** |  optional  | The host devices(comma separated) subject to the policy | string | 
**destination_zone** |  optional  | List of destinations zones(comma separated) for policy (default is Any) | string | 
**destination_device** |  optional  | List of host devices(comma separated) subject to the policy | string | 
**destination_address** |  optional  | List of destination addresses, address groups, or regions (default is Any) to be added to the policy | string | 
**negate_destination** |  optional  | Whether to negate the destination (apply the rule to destination addresses from the specified zone except for the addresses specified) | string | 
**application** |  optional  | List of specific applications(comma separated) for the Security policy rule | string | 
**service** |  optional  | List of services of the policy (comma separated, services to limit to specific TCP or UDP port numbers) | string | 
**category** |  optional  | List of URL Categories(comma separated) of the policy | string | 
**profile_setting** |  optional  | Type of profile setting to choose for the policy (additional checking that the firewall performs on packets that match the Security profile rule) | string | 
**action** |  optional  | Action the firewall takes on traffic that matches the attributes defined in a rule | string | 
**icmp_unreachable** |  optional  | Whether to send sent information to the client that a session is not allowed. Applicable only in case action is 'Drop', 'Reset Client', 'Reset Server', 'Reset Both' | string | 
**log_forwarding** |  optional  | To forward the local traffic log and threat log entries to remote destinations, such as Panorama | string | 
**target** |  optional  | Apply the rule to specific firewalls or descendant device groups of the Device Group (or Shared location) where the rule is defined (Takes serial number of firewall as input) | string | 
**disable** |  optional  | Whether to disable the policy | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.action | string |  |   allow 
action_result.parameter.application | string |  |   1c-enterprise 
action_result.parameter.audit_comment | string |  |   updated source address 
action_result.parameter.category | string |  |   Test URL Category 
action_result.parameter.description | string |  |   Policy rule to deny traffic from a specific address group 
action_result.parameter.destination_address | string |  |   dev_env_address_1  10.1.192.168 
action_result.parameter.destination_device | string |  |   test_device 
action_result.parameter.destination_zone | string |  |   IN 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.disable | string |  |   Yes 
action_result.parameter.icmp_unreachable | string |  |   Yes 
action_result.parameter.log_forwarding | string |  |   IoT Security Default Profile 
action_result.parameter.negate_destination | string |  |   Yes 
action_result.parameter.negate_source | string |  |   Yes 
action_result.parameter.policy_name | string |  `panorama policy name`  |   policy_rule_1 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.profile_setting | string |  |   profiles 
action_result.parameter.rule_type | string |  |   universal 
action_result.parameter.service | string |  |   service-http 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.source_address | string |  |   dev_env_address_1  10.1.192.168 
action_result.parameter.source_device | string |  |   test_device 
action_result.parameter.source_user | string |  |   test_user 
action_result.parameter.source_zone | string |  |   IN 
action_result.parameter.tag | string |  |   test_tag 
action_result.parameter.target | string |  |   000000000000000 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data.\*.@count | string |  |   1 
action_result.data.\*.@total-count | string |  |   1 
action_result.data.\*.entry.@admin | string |  |   admin 
action_result.data.\*.entry.@dirtyId | string |  |   153 
action_result.data.\*.entry.@loc | string |  |   do_not_delete_dg_child 
action_result.data.\*.entry.@name | string |  |   test_rule_23 
action_result.data.\*.entry.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.@uuid | string |  |   3fcfee47-4425-4c3a-8cb9-cb37ae4ee096 
action_result.data.\*.entry.action | string |  |   allow 
action_result.data.\*.entry.action.#text | string |  |   allow 
action_result.data.\*.entry.action.@admin | string |  |   admin 
action_result.data.\*.entry.action.@dirtyId | string |  |   153 
action_result.data.\*.entry.action.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.application.@admin | string |  |   admin 
action_result.data.\*.entry.application.@dirtyId | string |  |   153 
action_result.data.\*.entry.application.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.application.member | string |  |   any 
action_result.data.\*.entry.application.member.#text | string |  |   any 
action_result.data.\*.entry.application.member.@admin | string |  |   admin 
action_result.data.\*.entry.application.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.application.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.description.#text | string |  |   Case Sensitive Description. THIS is Case sensitive 
action_result.data.\*.entry.description.@admin | string |  |   admin 
action_result.data.\*.entry.description.@dirtyId | string |  |   153 
action_result.data.\*.entry.description.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.destination-hip.@admin | string |  |   admin 
action_result.data.\*.entry.destination-hip.@dirtyId | string |  |   153 
action_result.data.\*.entry.destination-hip.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.destination-hip.member | string |  |   any 
action_result.data.\*.entry.destination-hip.member.#text | string |  |   any 
action_result.data.\*.entry.destination-hip.member.@admin | string |  |   admin 
action_result.data.\*.entry.destination-hip.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.destination-hip.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.destination.@admin | string |  |   admin 
action_result.data.\*.entry.destination.@dirtyId | string |  |   153 
action_result.data.\*.entry.destination.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.destination.member | string |  |   any 
action_result.data.\*.entry.destination.member.#text | string |  |   any 
action_result.data.\*.entry.destination.member.@admin | string |  |   admin 
action_result.data.\*.entry.destination.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.destination.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.from.@admin | string |  |   admin 
action_result.data.\*.entry.from.@dirtyId | string |  |   153 
action_result.data.\*.entry.from.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.from.member | string |  |   any 
action_result.data.\*.entry.from.member.#text | string |  |   any 
action_result.data.\*.entry.from.member.@admin | string |  |   admin 
action_result.data.\*.entry.from.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.from.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.rule-type | string |  |   universal 
action_result.data.\*.entry.rule-type.#text | string |  |   universal 
action_result.data.\*.entry.rule-type.@admin | string |  |   admin 
action_result.data.\*.entry.rule-type.@dirtyId | string |  |   153 
action_result.data.\*.entry.rule-type.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.service.@admin | string |  |   admin 
action_result.data.\*.entry.service.@dirtyId | string |  |   153 
action_result.data.\*.entry.service.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.service.member | string |  |   any 
action_result.data.\*.entry.service.member.#text | string |  |   any 
action_result.data.\*.entry.service.member.\*.#text | string |  |   service-http 
action_result.data.\*.entry.service.member.\*.@admin | string |  |   admin 
action_result.data.\*.entry.service.member.\*.@dirtyId | string |  |   200 
action_result.data.\*.entry.service.member.\*.@time | string |  |   2023/09/25 07:16:26 
action_result.data.\*.entry.service.member.@admin | string |  |   admin 
action_result.data.\*.entry.service.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.service.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.source-hip.@admin | string |  |   admin 
action_result.data.\*.entry.source-hip.@dirtyId | string |  |   153 
action_result.data.\*.entry.source-hip.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.source-hip.member | string |  |   any 
action_result.data.\*.entry.source-hip.member.#text | string |  |   any 
action_result.data.\*.entry.source-hip.member.@admin | string |  |   admin 
action_result.data.\*.entry.source-hip.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.source-hip.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.source-user.@admin | string |  |   admin 
action_result.data.\*.entry.source-user.@dirtyId | string |  |   403 
action_result.data.\*.entry.source-user.@time | string |  |   2023/09/25 09:47:08 
action_result.data.\*.entry.source-user.member.#text | string |  |   do_not_delete_user_group_parent 
action_result.data.\*.entry.source-user.member.@admin | string |  |   admin 
action_result.data.\*.entry.source-user.member.@dirtyId | string |  |   403 
action_result.data.\*.entry.source-user.member.@time | string |  |   2023/09/25 09:47:08 
action_result.data.\*.entry.source.@admin | string |  |   admin 
action_result.data.\*.entry.source.@dirtyId | string |  |   153 
action_result.data.\*.entry.source.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.source.member | string |  |   any 
action_result.data.\*.entry.source.member.#text | string |  |   any 
action_result.data.\*.entry.source.member.\*.#text | string |  |   do_not_delete_address1_default 
action_result.data.\*.entry.source.member.\*.@admin | string |  |   admin 
action_result.data.\*.entry.source.member.\*.@dirtyId | string |  |   303 
action_result.data.\*.entry.source.member.\*.@time | string |  |   2023/09/25 08:52:12 
action_result.data.\*.entry.source.member.@admin | string |  |   admin 
action_result.data.\*.entry.source.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.source.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.to.@admin | string |  |   admin 
action_result.data.\*.entry.to.@dirtyId | string |  |   153 
action_result.data.\*.entry.to.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.entry.to.member | string |  |   any 
action_result.data.\*.entry.to.member.#text | string |  |   any 
action_result.data.\*.entry.to.member.\*.#text | string |  |   do_not_delete_zone1 
action_result.data.\*.entry.to.member.\*.@admin | string |  |   admin 
action_result.data.\*.entry.to.member.\*.@dirtyId | string |  |   403 
action_result.data.\*.entry.to.member.\*.@time | string |  |   2023/09/25 09:47:07 
action_result.data.\*.entry.to.member.@admin | string |  |   admin 
action_result.data.\*.entry.to.member.@dirtyId | string |  |   153 
action_result.data.\*.entry.to.member.@time | string |  |   2023/09/25 06:56:08 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.does_policy_exist.response.@code | string |  |   19 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result | string |  |  
action_result.summary.does_policy_exist.response.result.@count | string |  |   1 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   1 
action_result.summary.does_policy_exist.response.result.entry.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.@loc | string |  |   do_not_delete_dg_child 
action_result.summary.does_policy_exist.response.result.entry.@name | string |  |   test_rule_23 
action_result.summary.does_policy_exist.response.result.entry.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.@uuid | string |  |   3fcfee47-4425-4c3a-8cb9-cb37ae4ee096 
action_result.summary.does_policy_exist.response.result.entry.action | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.action.#text | string |  |   allow 
action_result.summary.does_policy_exist.response.result.entry.action.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.action.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.action.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.application.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.application.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.application.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.application.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.application.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.application.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.application.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.description.#text | string |  |   Case Sensitive Description. THIS is Case sensitive 
action_result.summary.does_policy_exist.response.result.entry.description.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.description.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.description.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.destination-hip.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.destination.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.destination.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.destination.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.destination.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.from.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.from.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.from.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.from.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.from.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.from.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.rule-type | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.rule-type.#text | string |  |   universal 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.rule-type.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.service.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.service.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.service.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.service.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.service.member.\*.#text | string |  |   service-http 
action_result.summary.does_policy_exist.response.result.entry.service.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.\*.@dirtyId | string |  |   200 
action_result.summary.does_policy_exist.response.result.entry.service.member.\*.@time | string |  |   2023/09/25 07:16:26 
action_result.summary.does_policy_exist.response.result.entry.service.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.service.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.service.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.source-hip.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.source-hip.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.source-user.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-user.@dirtyId | string |  |   403 
action_result.summary.does_policy_exist.response.result.entry.source-user.@time | string |  |   2023/09/25 09:47:08 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.#text | string |  |   do_not_delete_user_group_parent 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@dirtyId | string |  |   403 
action_result.summary.does_policy_exist.response.result.entry.source-user.member.@time | string |  |   2023/09/25 09:47:08 
action_result.summary.does_policy_exist.response.result.entry.source.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.source.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.source.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.#text | string |  |   do_not_delete_address1_default 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@dirtyId | string |  |   303 
action_result.summary.does_policy_exist.response.result.entry.source.member.\*.@time | string |  |   2023/09/25 08:52:12 
action_result.summary.does_policy_exist.response.result.entry.source.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.source.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.source.member.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.to.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.to.@time | string |  |   2023/09/25 06:56:08 
action_result.summary.does_policy_exist.response.result.entry.to.member | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.to.member.#text | string |  |   any 
action_result.summary.does_policy_exist.response.result.entry.to.member.\*.#text | string |  |   do_not_delete_zone1 
action_result.summary.does_policy_exist.response.result.entry.to.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.\*.@dirtyId | string |  |   403 
action_result.summary.does_policy_exist.response.result.entry.to.member.\*.@time | string |  |   2023/09/25 09:47:07 
action_result.summary.does_policy_exist.response.result.entry.to.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.to.member.@dirtyId | string |  |   153 
action_result.summary.does_policy_exist.response.result.entry.to.member.@time | string |  |   2023/09/25 06:56:08 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'move policy'
Move a security policy rule

Type: **generic**  
Read only: **False**

<p><h4>Action Keynote</h4><ul><li>If input for either 'dst_device_group' or 'dst_policy_type' is not given, the current device_group and current policy_type would be taken as their respective values.</li></ul></p>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**policy_name** |  required  | Name of the security policy rule (multiple policy names can be added in policy_name when they have to moved from one policy_type or device group to another(comma separated). Whereas, for changing their respective position internally in the same device group and policy_type, only one rule can be moved at a time.) | string |  `panorama policy name` 
**device_group** |  required  | Device group of the policy rule (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**policy_type** |  required  | Rule base of the policy (pre-rule or post-rule) | string | 
**dst_device_group** |  optional  | Device group to move the policy rule to (up to 31 characters) | string |  `panorama device group` 
**dst_policy_type** |  optional  | Rule base to move the policy to (pre-rule or post-rule) | string | 
**where** |  optional  | Where to position the policy, by default the policy would be created at the bottom | string | 
**dst** |  optional  | Policy in reference to which, position the current policy (inter dependent with 'where' parameter, when the value of where is 'before' or 'after', else it would be ignored) | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.dst | string |  |   test_policy_rule_1 
action_result.parameter.dst_device_group | string |  `panorama device group`  |   shared 
action_result.parameter.dst_policy_type | string |  |   pre-rulebase 
action_result.parameter.policy_name | string |  `panorama policy name`  |   policy_rule_1  policy_rule_1,policy_rule_2 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.where | string |  |   after 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@from | string |  |   /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='test_device_group_1_down']/pre-rulebase/security/rules 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.@to | string |  |   /config/shared/pre-rulebase/security/rules 
action_result.data.\*.response.member | string |  |   test_block_rule 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.id | string |  |   227 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   22:13:51 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/09/06 22:13:51 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/09/06 22:14:19 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   239 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   error 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn.entry.\*.#text | string |  |   { "uuid" : "e4ced49a-58db-40f5-aa5d-400bc1579da8", "serial" : "007951000393837", "rulename" : "test_rule_1", "ruletype" : "security", "vsys" : [{ "id" : "vsys1", "dgid" : 43, "shadowed-rule" : [ "Social Media Block", "test"]}]} 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn.entry.\*.@name | string |  |   e4ced49a-58db-40f5-aa5d-400bc1579da8 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   FAIL 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit failed 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/09/06 22:14:29 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   22:14:22 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   238 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   22:14:22 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/09/06 22:14:22 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/09/06 22:14:22 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.move policy rule.response.@code | string |  |   20 
action_result.summary.move policy rule.response.@from | string |  |   /config/shared/pre-rulebase/security/rules 
action_result.summary.move policy rule.response.@status | string |  |   success 
action_result.summary.move policy rule.response.@to | string |  |   /config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='test_device_group_1_down']/pre-rulebase/security/rules 
action_result.summary.move policy rule.response.member | string |  |   test_block_rule 
action_result.summary.move policy rule.response.msg | string |  |   command succeeded 
action_result.message | string |  |   Successfully moved policy 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'delete policy'
Delete a security policy rule

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**policy_name** |  required  | Name of the policy rule to delete | string |  `panorama policy name` 
**policy_type** |  required  | Rule base to delete the policy from (pre-rule or post-rule) | string | 
**device_group** |  required  | Device group of the policy rule (default is 'shared') | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.policy_name | string |  `panorama policy name`  |   policy_rule_1 
action_result.parameter.policy_type | string |  |   pre-rulebase 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.id | string |  |   640 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   03:31:30 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/08/29 03:31:30 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/08/29 03:31:54 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings | string |  |  
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@cmd | string |  |   push-data 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dgname | string |  |   test_device_group 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@dname | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@jobid | string |  |   214 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@result | string |  |   error 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.@tplname | string |  |   test_template_stack 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.app-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn.entry.\*.#text | string |  |   { "uuid" : "e4ced49a-58db-40f5-aa5d-400bc1579da8", "serial" : "007951000393837", "rulename" : "test_rule_1", "ruletype" : "security", "vsys" : [{ "id" : "vsys1", "dgid" : 43, "shadowed-rule" : [ "Social Media Block", "test"]}]} 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.shadow-warn.entry.\*.@name | string |  |   e4ced49a-58db-40f5-aa5d-400bc1579da8 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.details.msg.warnings.line | string |  |   External Dynamic List test65432 is configured with no certificate profile. Please select a certificate profile for performing server certificate validation. 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.devicename | string |  |   PA-VM 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.multi-vsys | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.result | string |  |   FAIL 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.serial-no | string |  |   007951000393837 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.status | string |  |   commit failed 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tfin | string |  |   2023/09/06 22:12:56 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.tstart | string |  |   22:12:50 
action_result.summary.commit_device_groups.\*.finished_job.devices.entry.vsys | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   dg1 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   651 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   03:31:57 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/08/29 03:31:57 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/08/29 03:31:57 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'create address group'
Create an address group

Type: **contain**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of the address group to be created (up to 63 characters) | string |  `panorama address group name` 
**device_group** |  required  | Device group to create the address group in or 'shared' (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**type** |  required  | Type of the address group (Whether to create a static or a dynamic address group) | string | 
**addresses_or_match_criteria** |  required  | List of addresses or address_group to add in this address group, if 'type' is static then addresses or address groups to be included in address group have to added and if 'type' is dynamic then the match criteria (using 'and' or 'or' operators with different tags available in that device group, negation is not supported) to add addresses and address groups that satisfy this criteria into this newly created address group has to be added | string | 
**description** |  optional  | Description for the address group (max length 1023 characters) | string | 
**disable_override** |  optional  | Used to ensure that a firewall administrator cannot override settings locally on a firewall that inherits this configuration through a Device Group commit from Panorama (only used when device group is not 'shared') | string | 
**tag** |  optional  | List of tags to apply to this address group (allow to group objects using keywords or phrases, max length 127 characters) | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.addresses_or_match_criteria | string |  |   address_1,address_2  'tag_1' and 'tag_2' or 'tag_3' 
action_result.parameter.description | string |  |   Test description 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.disable_override | string |  |   Yes 
action_result.parameter.name | string |  `panorama address group name`  |   address_group_1 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.tag | string |  |   tag_1,tag_2 
action_result.parameter.type | string |  |   Static 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data.\*.@count | string |  |   0 
action_result.data.\*.@total-count | string |  |   0 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.does_policy_exist.response.@code | string |  |   7 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result | string |  |  
action_result.summary.does_policy_exist.response.result.@count | string |  |   0 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   0 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'modify address group'
Modify an address group

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of the address group to be modified | string |  `panorama address group name` 
**device_group** |  required  | Device group to which the address group to be modified belongs (default is 'shared') | string |  `panorama device group` 
**type** |  optional  | Type of the address group | string | 
**addresses_or_match_criteria** |  optional  | List of addresses or address_group to add in this address group, if 'type' is static then addresses or address groups to be included in address group have to added and if 'type' is dynamic then the match criteria (using 'and' or 'or' operators with different tags available in that device group, negation is not supported) to add addresses and address groups that satisfy this criteria into this newly created address group has to be added | string | 
**description** |  optional  | Description for the address group (max length 1023 characters) | string | 
**disable_override** |  optional  | Used to ensure that a firewall administrator cannot override settings locally on a firewall that inherits this configuration through a Device Group commit from Panorama (only used when device group is not 'shared') | string | 
**tag** |  optional  | List of tags to apply to this address group (allow to group objects using keywords or phrases, max length 127 characters) | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.addresses_or_match_criteria | string |  |   address_1,address_2  'tag_1' and 'tag_2' or 'tag_3' 
action_result.parameter.description | string |  |   Test description 
action_result.parameter.device_group | string |  `panorama device group`  |   shared 
action_result.parameter.disable_override | string |  |   Yes 
action_result.parameter.name | string |  `panorama address group name`  |   address_group_1 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.tag | string |  |   tag_1,tag_2 
action_result.parameter.type | string |  |   Static 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data.\*.@count | string |  |   1 
action_result.data.\*.@total-count | string |  |   1 
action_result.data.\*.entry.@admin | string |  |   admin 
action_result.data.\*.entry.@dirtyId | string |  |   6 
action_result.data.\*.entry.@loc | string |  |   New_Device_Group_1234 
action_result.data.\*.entry.@name | string |  |   New_address_Group1234 
action_result.data.\*.entry.@time | string |  |   2023/10/03 23:06:06 
action_result.data.\*.entry.description.#text | string |  |   This is test description for Address_group 
action_result.data.\*.entry.description.@admin | string |  |   admin 
action_result.data.\*.entry.description.@dirtyId | string |  |   6 
action_result.data.\*.entry.description.@time | string |  |   2023/10/03 23:06:06 
action_result.data.\*.entry.static.@admin | string |  |   admin 
action_result.data.\*.entry.static.@dirtyId | string |  |   6 
action_result.data.\*.entry.static.@time | string |  |   2023/10/03 23:06:07 
action_result.data.\*.entry.static.member.#text | string |  |   do_not_delete_address_group_shared 
action_result.data.\*.entry.static.member.@admin | string |  |   admin 
action_result.data.\*.entry.static.member.@dirtyId | string |  |   6 
action_result.data.\*.entry.static.member.@time | string |  |   2023/10/03 23:06:07 
action_result.data.\*.entry.tag.@admin | string |  |   admin 
action_result.data.\*.entry.tag.@dirtyId | string |  |   6 
action_result.data.\*.entry.tag.@time | string |  |   2023/10/03 23:06:06 
action_result.data.\*.entry.tag.member.#text | string |  |   test_tag1 
action_result.data.\*.entry.tag.member.@time | string |  |   2023/10/04 01:05:29 
action_result.data.\*.entry.tag.member.@admin | string |  |   admin 
action_result.data.\*.entry.tag.member.@dirtyId | string |  |   8 
action_result.data.\*.entry.tag.member.\*.#text | string |  |   Test_Tag_For_ADG 
action_result.data.\*.entry.tag.member.\*.@admin | string |  |   admin 
action_result.data.\*.entry.tag.member.\*.@dirtyId | string |  |   6 
action_result.data.\*.entry.tag.member.\*.@time | string |  |   2023/10/03 23:06:06 
action_result.data.\*.response.@code | string |  |   20 
action_result.data.\*.response.@status | string |  |   success 
action_result.data.\*.response.msg | string |  |   command succeeded 
action_result.summary.does_policy_exist.response.result.entry.tag.member.#text | string |  |   test_tag1 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@time | string |  |   2023/10/04 01:05:29 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.@dirtyId | string |  |   8 
action_result.summary.does_policy_exist.response.@code | string |  |   19 
action_result.summary.does_policy_exist.response.@status | string |  |   success 
action_result.summary.does_policy_exist.response.result | string |  |  
action_result.summary.does_policy_exist.response.result.@count | string |  |   1 
action_result.summary.does_policy_exist.response.result.@total-count | string |  |   1 
action_result.summary.does_policy_exist.response.result.entry.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.@loc | string |  |   New_Device_Group_1234 
action_result.summary.does_policy_exist.response.result.entry.@name | string |  |   New_address_Group1234 
action_result.summary.does_policy_exist.response.result.entry.@time | string |  |   2023/10/03 23:06:06 
action_result.summary.does_policy_exist.response.result.entry.description.#text | string |  |   This is test description for Address_group 
action_result.summary.does_policy_exist.response.result.entry.description.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.description.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.description.@time | string |  |   2023/10/03 23:06:06 
action_result.summary.does_policy_exist.response.result.entry.static.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.static.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.static.@time | string |  |   2023/10/03 23:06:07 
action_result.summary.does_policy_exist.response.result.entry.static.member.#text | string |  |   do_not_delete_address_group_shared 
action_result.summary.does_policy_exist.response.result.entry.static.member.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.static.member.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.static.member.@time | string |  |   2023/10/03 23:06:07 
action_result.summary.does_policy_exist.response.result.entry.tag.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.@time | string |  |   2023/10/03 23:06:06 
action_result.summary.does_policy_exist.response.result.entry.tag.member.\*.#text | string |  |   Test_Tag_For_ADG 
action_result.summary.does_policy_exist.response.result.entry.tag.member.\*.@admin | string |  |   admin 
action_result.summary.does_policy_exist.response.result.entry.tag.member.\*.@dirtyId | string |  |   6 
action_result.summary.does_policy_exist.response.result.entry.tag.member.\*.@time | string |  |   2023/10/03 23:06:06 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list address groups'
List the address groups

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**device_group** |  required  | Device group whose address groups you want to list (up to 31 characters, default is 'shared') | string |  `panorama device group` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.data.\*.@admin | string |  |   admin 
action_result.data.\*.@dirtyId | string |  |   1 
action_result.data.\*.@name | string |  `panorama address group name`  |   test address group name 
action_result.data.\*.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.description | string |  |   test 
action_result.data.\*.description.#text | string |  |   test 
action_result.data.\*.description.@admin | string |  |   admin 
action_result.data.\*.description.@dirtyId | string |  |   1 
action_result.data.\*.description.@time | string |  |   2023/09/24 22:58:19 
action_result.data.\*.disable-override | string |  |   Yes 
action_result.data.\*.dynamic.filter | string |  |   blocked 
action_result.data.\*.static | string |  |  
action_result.data.\*.static.@admin | string |  |   admin 
action_result.data.\*.static.@dirtyId | string |  |   1 
action_result.data.\*.static.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.static.member | string |  |   2.2.2.2 Added By User 
action_result.data.\*.static.member.#text | string |  |   test1 
action_result.data.\*.static.member.\*.#text | string |  |   test_address_tag 
action_result.data.\*.static.member.\*.@admin | string |  |   admin 
action_result.data.\*.static.member.\*.@dirtyId | string |  |   1 
action_result.data.\*.static.member.\*.@time | string |  |   2023/09/24 22:58:19 
action_result.data.\*.static.member.@admin | string |  |   admin 
action_result.data.\*.static.member.@dirtyId | string |  |   1 
action_result.data.\*.static.member.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.tag.@admin | string |  |   admin 
action_result.data.\*.tag.@dirtyId | string |  |   1 
action_result.data.\*.tag.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.tag.member | string |  |   xyz 
action_result.data.\*.tag.member.#text | string |  |   from_ui 
action_result.data.\*.tag.member.\*.#text | string |  |   new 
action_result.data.\*.tag.member.\*.@admin | string |  |   admin 
action_result.data.\*.tag.member.\*.@dirtyId | string |  |   1 
action_result.data.\*.tag.member.\*.@time | string |  |   2023/09/24 22:58:19 
action_result.data.\*.tag.member.@admin | string |  |   admin 
action_result.data.\*.tag.member.@dirtyId | string |  |   1 
action_result.data.\*.tag.member.@time | string |  |   2023/09/24 23:15:36 
action_result.summary.total_address_groups | numeric |  |   1 
action_result.message | string |  |   Total address groups: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get address group'
Fetch address group details for the supplied address group name

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of address group (up to 63 characters) | string |  `panorama address group name` 
**device_group** |  required  | Device group in which the address group exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.parameter.name | string |  `panorama address group name`  |   test_address_group_name 
action_result.data.\*.@admin | string |  |   admin 
action_result.data.\*.@dirtyId | string |  |   1 
action_result.data.\*.@loc | string |  |   test 
action_result.data.\*.@name | string |  |   test 
action_result.data.\*.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.description | string |  |   test 
action_result.data.\*.static.@admin | string |  |   admin 
action_result.data.\*.static.@dirtyId | string |  |   1 
action_result.data.\*.static.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.static.member.#text | string |  |   test1 
action_result.data.\*.static.member.@admin | string |  |   admin 
action_result.data.\*.static.member.@dirtyId | string |  |   1 
action_result.data.\*.static.member.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.tag.@admin | string |  |   admin 
action_result.data.\*.tag.@dirtyId | string |  |   1 
action_result.data.\*.tag.@time | string |  |   2023/09/24 23:15:36 
action_result.data.\*.tag.member.#text | string |  |   from_ui 
action_result.data.\*.tag.member.@admin | string |  |   admin 
action_result.data.\*.tag.member.@dirtyId | string |  |   1 
action_result.data.\*.tag.member.@time | string |  |   2023/09/24 23:15:36 
action_result.summary | string |  |  
action_result.message | string |  |   Successfully fetched address group details 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'delete address group'
Delete an address group for the supplied address group name

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of address group (up to 63 characters) | string |  `panorama address group name` 
**device_group** |  required  | Device group in which the address group exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.parameter.name | string |  `panorama address group name`  |   test_address_group_name 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'create address'
Create an address on the panorama platform

Type: **contain**  
Read only: **False**

<p><h4>Action Keynote</h4><ul><li>The 'ip' paramater support 4-type of ip address object as follow. <ol><li>IP Netmask—Enter the IPv4 or IPv6 address or IP address range using the following notation: ip_address/mask or ip_address where the mask is the number of significant binary digits used for the network portion of the address. Ideally, for IPv6 addresses, you specify only the network portion, not the host portion. For example:</li><ul><li>192.168.80.150/32—Indicates one address.</li><li>192.168.80.0/24—Indicates all addresses from 192.168.80.0 through 192.168.80.255.</li><li>2001:db8::/32</li><li>2001:db8:123:1::/64</li></ul><li>IP Range—Enter a range of addresses using the following format: ip_address-ip_address where both ends of the range are IPv4 addresses or both are IPv6 addresses. For example: 2001:db8:123:1::1-2001:db8:123:1::22</li><li>IP Wildcard Mask—Enter an IP wildcard address in the format of an IPv4 address followed by a slash and a mask (which must begin with a zero); for example, 10.182.1.1/0.127.248.0. In the wildcard mask, a zero (0) bit indicates that the bit being compared must match the bit in the IP address that is covered by the 0. A one (1) bit in the mask is a wildcard bit, meaning the bit being compared need not match the bit in the IP address that is covered by the 1. Convert the IP address and the wildcard mask to binary. To illustrate the matching: on binary snippet 0011, a wildcard mask of 1010 results in four matches (0001, 0011, 1001, and 1011).<ul><li>Note - You can use an address object of type IP Wildcard Mask only in a Security policy rule.</li></ul></li><li>FQDN—Enter the domain name. The FQDN initially resolves at commit time. An FQDN entry is subsequently refreshed based on the TTL of the FQDN if the TTL is greater than or equal to the Minimum FQDN Refresh Time; otherwise the FQDN entry is refreshed at the Minimum FQDN Refresh Time. The FQDN is resolved by the system DNS server or a DNS proxy object if a proxy is configured.</li></ol></li></p>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of address to be created (up to 63 characters) | string |  `panorama address name` 
**device_group** |  required  | Device group in which you want to create address (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**type** |  required  | Type of address to create | string | 
**value** |  required  | Value of address as per the selected type | string |  `ip`  `ipv6`  `domain`  `panorama address value` 
**description** |  optional  | Description of address (up to 1023 characters) | string | 
**tag** |  optional  | Tags want to apply on an address (comma-separated, up to 127 characters for each tag) | string | 
**disable_override** |  optional  | Whether to disable override the address or not | string | 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.data | string |  |  
action_result.parameter.description | string |  |   Test description 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.parameter.disable_override | string |  |   Yes 
action_result.parameter.name | string |  `panorama address name`  |   test_address_name 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.tag | string |  |   test_address_tag 
action_result.parameter.type | string |  |   IP Netmask 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.value | string |  `ip`  `ipv6`  `domain`  `panorama address value`  |   10.1.1.1 
action_result.data.\*.@count | string |  |   0 
action_result.data.\*.@total-count | string |  |   0 
action_result.summary.commit_config.finished_job.description | string |  |  
action_result.summary.commit_config.finished_job.details.line | string |  |   Configuration committed successfully 
action_result.summary.commit_config.finished_job.id | string |  |   622 
action_result.summary.commit_config.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_config.finished_job.progress | string |  |   100 
action_result.summary.commit_config.finished_job.queued | string |  |   No 
action_result.summary.commit_config.finished_job.result | string |  |   OK 
action_result.summary.commit_config.finished_job.status | string |  |   FIN 
action_result.summary.commit_config.finished_job.stoppable | string |  |   No 
action_result.summary.commit_config.finished_job.tdeq | string |  |   03:06:14 
action_result.summary.commit_config.finished_job.tenq | string |  |   2023/09/11 03:06:14 
action_result.summary.commit_config.finished_job.tfin | string |  |   2023/09/11 03:06:40 
action_result.summary.commit_config.finished_job.type | string |  |   Commit 
action_result.summary.commit_config.finished_job.user | string |  |   admin 
action_result.summary.commit_config.finished_job.warnings.line | string |  |   HA Peer Serial Number has not been entered. Please enter the serial number of the HA peer. 
action_result.summary.commit_device_groups.\*.finished_job.description | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.devices | string |  |  
action_result.summary.commit_device_groups.\*.finished_job.dgname | string |  |   share 
action_result.summary.commit_device_groups.\*.finished_job.id | string |  |   633 
action_result.summary.commit_device_groups.\*.finished_job.positionInQ | string |  |   0 
action_result.summary.commit_device_groups.\*.finished_job.progress | string |  |   100 
action_result.summary.commit_device_groups.\*.finished_job.push_type | string |  |   shared-policy 
action_result.summary.commit_device_groups.\*.finished_job.queued | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.result | string |  |   OK 
action_result.summary.commit_device_groups.\*.finished_job.sched | string |  |   None 
action_result.summary.commit_device_groups.\*.finished_job.status | string |  |   FIN 
action_result.summary.commit_device_groups.\*.finished_job.stoppable | string |  |   No 
action_result.summary.commit_device_groups.\*.finished_job.tdeq | string |  |   03:06:43 
action_result.summary.commit_device_groups.\*.finished_job.tenq | string |  |   2023/09/11 03:06:43 
action_result.summary.commit_device_groups.\*.finished_job.tfin | string |  |   2023/09/11 03:06:43 
action_result.summary.commit_device_groups.\*.finished_job.type | string |  |   CommitAll 
action_result.summary.commit_device_groups.\*.finished_job.user | string |  |   admin 
action_result.summary.commit_device_groups.\*.finished_job.warnings | string |  |  
action_result.summary.create_address.response.@code | string |  |   20 
action_result.summary.create_address.response.@status | string |  |   success 
action_result.summary.create_address.response.msg | string |  |   command succeeded 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get address'
Fetch address details for the supplied address name

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of address (up to 63 characters) | string |  `panorama address name` 
**device_group** |  required  | Device group in which the address exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.parameter.name | string |  `panorama address name`  |   test_address_name 
action_result.data.\*.@admin | string |  |   admin 
action_result.data.\*.@dirtyId | string |  |   175 
action_result.data.\*.@loc | string |  |   dg1 
action_result.data.\*.@name | string |  |   test 
action_result.data.\*.@time | string |  |   2023/09/13 05:18:32 
action_result.data.\*.description | string |  |   Test 
action_result.data.\*.description.#text | string |  |   testing with , 
action_result.data.\*.description.@admin | string |  |   admin 
action_result.data.\*.description.@dirtyId | string |  |   25 
action_result.data.\*.description.@time | string |  |   2023/09/26 23:49:56 
action_result.data.\*.disable-override | string |  |   No 
action_result.data.\*.disable-override.#text | string |  |   No 
action_result.data.\*.disable-override.@admin | string |  |   admin 
action_result.data.\*.disable-override.@dirtyId | string |  |   175 
action_result.data.\*.disable-override.@time | string |  |   2023/09/13 05:18:32 
action_result.data.\*.ip-netmask | string |  |   10.1.1.1 
action_result.data.\*.ip-netmask.#text | string |  |   10.1.1.1 
action_result.data.\*.ip-netmask.@admin | string |  |   admin 
action_result.data.\*.ip-netmask.@dirtyId | string |  |   175 
action_result.data.\*.ip-netmask.@time | string |  |   2023/09/13 05:18:32 
action_result.data.\*.tag.member.#text | string |  |   test_tag1 
action_result.data.\*.tag.member.@time | string |  |   2023/10/05 23:22:27 
action_result.data.\*.tag.member.@admin | string |  |   user1 
action_result.data.\*.tag.member.@dirtyId | string |  |   46 
action_result.data.\*.tag.member | string |  |   test_tag1 
action_result.data.\*.ip-wildcard.#text | string |  |   10.20.1.0/0.0.248.255 
action_result.data.\*.ip-wildcard.@time | string |  |   2023/10/19 04:16:04 
action_result.data.\*.ip-wildcard.@admin | string |  |   admin 
action_result.data.\*.ip-wildcard.@dirtyId | string |  |   322 
action_result.data.\*.ip-range.#text | string |  |   12.12.12.12-13.13.13.13 
action_result.data.\*.ip-range.@time | string |  |   2023/10/19 04:16:05 
action_result.data.\*.ip-range.@admin | string |  |   admin 
action_result.data.\*.ip-range.@dirtyId | string |  |   322 
action_result.data.\*.fqdn.#text | string |  |   www.google.com 
action_result.data.\*.fqdn.@time | string |  |   2023/10/19 04:16:06 
action_result.data.\*.fqdn.@admin | string |  |   admin 
action_result.data.\*.fqdn.@dirtyId | string |  |   322 
action_result.data.\*.tag.@admin | string |  |   admin 
action_result.data.\*.tag.@dirtyId | string |  |   25 
action_result.data.\*.tag.@time | string |  |   2023/09/26 23:49:56 
action_result.data.\*.tag.member.\*.#text | string |  |   avs 
action_result.data.\*.tag.member.\*.@admin | string |  |   admin 
action_result.data.\*.tag.member.\*.@dirtyId | string |  |   25 
action_result.data.\*.tag.member.\*.@time | string |  |   2023/09/26 23:49:56 
action_result.summary | string |  |  
action_result.message | string |  |   Successfully fetched address details 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'delete address'
Delete address details for the supplied address name

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name of address (up to 63 characters) | string |  `panorama address name` 
**device_group** |  required  | Device group in which the address exists (up to 31 characters, default is 'shared') | string |  `panorama device group` 
**should_commit_changes** |  optional  | Whether to commit both, changes to firewall and changes to device groups at the end of this action | boolean | 
**use_partial_commit** |  optional  | Whether to perform user specific commit. As part of the request, the configuration's username is included as the administrator name (when the 'should_commit_changes' is 'false' the 'use_partial_commit' parameter is ignored) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.device_group | string |  `panorama device group`  |   test_device_grp 
action_result.parameter.name | string |  `panorama address name`  |   test_address_name 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary.delete_address.response.@code | string |  |   20 
action_result.summary.delete_address.response.@status | string |  |   success 
action_result.summary.delete_address.response.msg | string |  |   command succeeded 
action_result.message | string |  |   Response Received: command succeeded 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 