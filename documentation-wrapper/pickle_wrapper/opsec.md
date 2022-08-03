+++
title = "OPSEC"
chapter = false
weight = 10
pre = "<b>1. </b>"
+++

### Execution
The service will not block the pickle from working in it's original solution. It will spawn a new thread though so the original process may seem to hang after execution if the agent is still running. As such you should pivot out of this agent if you injected into a model that is simply doign a single inference or will otherwise only run for a short period of time. If you inject into a model that will be used for transfer learning, that will likely be a longer lived process and as such you may not need to pivot as quickly.