# Pickle Injection Wrapper
The `pickle_wrapper` payload is a special payload. This is a python encoder that acts as a "wrapper" around a Medusa agent (any python agent should work). As such, this payload type has no commands and no supported C2 profiles - it simply acts as a way to turn arbitrary other agents into pickle op codes and injects that into a specified Pickle.

![dmeo image](https://coldwaterq.com/presentations/ColdwaterQ%20-%20BACKDOORING%20Pickles%20A%20decade%20only%20made%20things%20worse%20-%20v1%20-%20demo.gif)

To use it you upload a pickle to mythic, and while generating the wrapper, put the name into the appropriate field and pick an agent to wrap. Besides that everything is handled for you.

## Setup

## How to install an agent in this format within Mythic

In order to install the agent, it's pretty simple. Within Mythic you can run the `mythic-cli` binary to install this in one of three ways:

* `./mythic-cli install github https://github.com/MythicAgents/pickle_wrapper` to install the main branch
* `./mythic-cli install github https://github.com/MythicAgents/pickle_wrapper branchname` to install a specific branch of that repo
* `./mythic-cli install folder /path/to/local/folder/cloned/from/github` to install from an already cloned down version of an agent repo

## Updates to get things working
Medusa needs to be updated to support pickle_wrapper.
```diff
diff --git a/Payload_Type/medusa/mythic/agent_functions/builder.py b/Payload_Type/medusa/mythic/agent_functions/builder.py
index 61fdeba..801c83e 100644
--- a/Payload_Type/medusa/mythic/agent_functions/builder.py
+++ b/Payload_Type/medusa/mythic/agent_functions/builder.py
@@ -16,7 +16,7 @@ class Medusa(PayloadType):
         SupportedOS.Windows, SupportedOS.Linux, SupportedOS.MacOS
     ]
     wrapper = False
-    wrapped_payloads = []
+    wrapped_payloads = ["pickle_wrapper"]
     mythic_encrypts = True
     note = "This payload uses Python to create a simple agent"
     supports_dynamic_loading = True
```

if you get `RECONDITION_FAILED - message size XXXXXXX is larger than configured max size 134217728"`
edit Mythic/rabbitmq-docker/rabbitmq.conf to add the following line
`max_message_size = 536870911`
This is caused when injecting an agent into a pickled file that is larger than approximately 100MB. This sets the maximum to it's complete maximum, and will still only handle 500MB, so another solution is being sought out.

## Icon

https://publicdomainvectors.org/en/free-clipart/Pickle/44539.html

<a href="https://publicdomainvectors.org/en/free-clipart/Pickle/44539.html" title="pickle emogi">Pickle emogi - Public Domain vectors</a>

## Development
If you are testing on Windows and need to start the http listenner
1. After starting mythic edit `docker-compose.yml`
 - Under the HTTP service delete `network_mode: host` and `extra_hosts:` as well as the two lines start with `-` after `extra_hosts:`
 - Add
 ```
  networks:
    - default_network
```
2. Run `sudo ./mythic-cli mythic start http`



### Detection
- [Yara Rule created by Medsterr](https://github.com/medsterr/yara/tree/main/python/pickle_injector)

### Related Presentation
- [DEFCON Powerpoint Version](https://coldwaterq.com/presentations/ColdwaterQ%20-%20BACKDOORING%20Pickles%20A%20decade%20only%20made%20things%20worse%20-%20v1.pptx)
- [DEFCON PDF Version](https://coldwaterq.com/presentations/ColdwaterQ%20-%20BACKDOORING%20Pickles%20A%20decade%20only%20made%20things%20worse%20-%20v1.pdf)
