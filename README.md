# AITestingProject
This repository marks my solution to the *Sebaka* AI Testing Hackathon.

## The problem
Many companies and organisations are in a rush to integrate AI into their systems, whether as a product, a support tool, or a database query assistant. This has created a new wave of vulnerabilities that can be extremely costly. These include prompt injections, jailbreaking, hallucinations, and inaccurate information output. The overall volume and surface area of AI exploits is increasing.

What makes this problem even more complicated is that software testers are seldom given enough time to rigorously test against all potential test cases for vulnerabilities. On top of that, the search space for AI systems is effectively infinite and probabilistic, so one test may not accurately reflect the underlying risk.

Additionally, in order to actually see where an AI system fails, one has to continuously create many different variations of a certain prompt and test them to see if they fail. But creating many prompt variations is not a job for humans; it is a job for AI.

This is where a swarm comes in. We have to fight fire with fire. Using AI as an orchestrator to create many subagents that try to break the AI, we can identify weak points before it goes into production.