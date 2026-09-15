# AITestingProject
This repository marks is for my solution to the *Sebaka* AI -testing Hackathon

## The problem
Many companies and orgainsationas are in a rush to integrate AI into their system, either as a product, as support or int eh database query. This has created a new wave of vulnerabilities which are very costly. these include prompt injections, jailbreaking, hallucinations and inaccurate information output. The overall volume and surface area of AI exploits is increasing. 

What makes this problem even more complicated, is that software testers are seldom given enough time to rogoriously test against all test cases to check for vulnerabilities. On toop of that the search space for AI systems is infinite and probabilisitc, so one test may not actually give you an accurate result of the underlying risk.

Additionally in order to actually see where an AI system fails, on has to continuously create many different variations of a cartain prompt and test those in order to see if it fails. But creating many different variations of prompts is not a job for humans but a job for AI.

This is where swarm comes in. We have to fight fire with fire. Using AI as an orchestrator to create many subagents that try to break the AI , we can see the weak point before it goes into production.