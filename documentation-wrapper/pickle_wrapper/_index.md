+++
title = "pickle_wrapper"
chapter = false
weight = 5
+++

## Summary

The `pickle_wrapper` payload injects the agent into an existing pickle. It takes in another agent, probably a `medusa` agent, and a file to inject the agent into. The build process checks if the target file contains valid pickles and will error if it isn't.
The wrapper will find a random location in the pickle and inject the agent into it, so the resulting output will be the target pickle with the agent added into it.

### Highlighted wrapper Features
- Adds a python agent into a pickle

### File extensions that are typically pickles
- pth
- pt
- pkl

## Authors
- @coldwaterq
