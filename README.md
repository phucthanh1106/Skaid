# Project Overview
- This Raspberry Pi Cluster will host a LLM model that will be trained on notes from different CS classes so that students can use that LLM to 
help them study and query information about the class. Moreover, the LLM will only answer to questions regarding a class's materials and NOT provide any
solution to exam's or homework's questions. What it can do is to help student understand the problem/question or suggest some approach. This is somewhat
similar to the AI tool provided in Microsoft's OA which only provides answers to a language's syntax or help the test taker understand the problem that was assigned
to them.

## Message Queue
- First, I will only be working with 2 Pis first such that Pi 2 will be the master (distribute prompts to worker) and Pi 3 will be the worker (work on the propmts by using LLM to generate responses). 
Later on, when I feel like I'm more capable, I will scale this project to use up to 5 Pis or even maybe 10+ Pis. 
- The initial plan is to make a frontend and a backend with 2 main queues (toLLM and fromLLM):
    + toLLM will hold the prompts from the students
    + fromLLM will hold the responses to the prompts from toLLM
- More specifically, here is the flow of frontend and backend:
    + FE will first capture the prompt from a student screen and put it into the toLLM queue. 
    Later on when a response to that prompt is generated, FE will get the response from the fromLLM queue to display it on the student's screen.
    + BE will take prompts from the toLLM queue and call the LLM model to work on it. After the job finishes, BE puts that response into the fromLLM queue.