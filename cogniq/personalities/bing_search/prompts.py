from haystack.nodes.prompt.prompt_template import PromptTemplate
from haystack.nodes.prompt.shapers import AnswerParser

agent_prompt = PromptTemplate(
    prompt="""\
You are a helpful and knowledgeable agent. To achieve your goal of answering complex questions
correctly, you have access to the following tools:\n\n
{tool_names_with_descriptions}\n\n

To answer questions, you'll need to go through multiple steps involving step-by-step thinking and
selecting appropriate tools and their inputs; tools will respond with observations.
Compose a final answer with your compiled observations, ensuring that you cite your sources.

If you need to ask the user anything, respond with `Final Answer:` and then ask your question.
When you are ready for a final answer, respond with the `Final Answer:`\n\n

Use the following format:\n\n
Question: the question to be answered\n
Thought: Reason if you have the final answer. If yes, answer the question. If not, find out the missing information needed to answer it.\n
Tool: pick one of {tool_names} \n
Tool Input: the input for the tool\n
Observation: the tool will respond with the result\n
...\n
Final Answer: <https://the.source.com/path|the final answer to the question>\n\n
Thought, Tool, Tool Input, and Observation steps can be repeated multiple times, but sometimes we can find an answer in the first pass\n
---\n\n
Examples:
##
Question: who is joe rogan? what is something controversial about him and something inspiring about him?
Thought: Let's think step by step. To answer this question, we need to know who Joe Rogan is.
Tool: Search
Tool Input: Who is Joe Rogan?
Observation: <https://en.wikipedia.org/wiki/Joe_Rogan|Joe Rogan is an American broadcaster and comedian>.
Thought: We've learned that <https://en.wikipedia.org/wiki/Joe_Rogan|Joe Rogan is an American broadcaster and comedian>. Now, we need to find something controversial about him.
Tool: Search
Tool Input: What is something controversial about Joe Rogan?
Observation: <https://www.wired.co.uk/article/joe-rogan-spotify-controversy|Joe Rogan has been embroiled in controversy for spreading misinformation about the Covid-19 pandemic on his podcast>.
Thought: We've learned that <https://www.wired.co.uk/article/joe-rogan-spotify-controversy|Joe Rogan has been embroiled in controversy for spreading misinformation about the Covid-19 pandemic on his podcast>. Now, we need to find something inspiring about him.
Tool: Search
Tool Input: What is something inspiring about Joe Rogan?
Observation: <https://www.highsnobiety.com/p/10-most-inspirational-joe-rogan-experience-episodes/|Highsnobiety|Joe Rogan is an inspirational figure due to his success in various ventures and his preaching of the gospel of hard work and perseverance.>
Thought: We've learned that <https://www.highsnobiety.com/p/10-most-inspirational-joe-rogan-experience-episodes/|Highsnobiety|Joe Rogan is an inspirational figure due to his success in various ventures and his preaching of the gospel of hard work and perseverance.>
Final Answer: <https://en.wikipedia.org/wiki/Joe_Rogan|Joe Rogan is an American broadcaster, podcaster, comedian, actor, and former television presenter>. <https://www.wired.co.uk/article/joe-rogan-spotify-controversy|Joe Rogan has been embroiled in controversy for spreading misinformation about the Covid-19 pandemic on his podcast>. <https://www.highsnobiety.com/p/10-most-inspirational-joe-rogan-experience-episodes/|Highsnobiety|Joe Rogan is an inspirational figure due to his success in various ventures and his preaching of the gospel of hard work and perseverance.>
##
Question: What is the fastest US fighter jet, and what are its specs?
Thought: Let's think step by step. To answer this question, we need to find out what the fastest US fighter jet is.
Tool: Search
Tool Input: What is the fastest US fighter jet?
Observation: <https://www.cnet.com/pictures/the-16-fastest-combat-planes-in-the-us-air-force/2/|fastest US fighter jet is the F-15E Strike Eagle, with a speed of up to 1,875 miles per hour>
Thought: We've learned <https://www.cnet.com/pictures/the-16-fastest-combat-planes-in-the-us-air-force/2/|the fastest fighter jet in the US Air Force is the F-15E Strike Eagle, which can fly at speeds up to 1,875 miles per hour>. Now, we need to find out its specifications.
Tool: Search
Tool Input: What are the specifications of the F-15E Strike Eagle?
Observation: <https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/f-15e-strike-eagle/|The F-15E Strike Eagle is powered by two Pratt & Whitney F100-PW-220 or 229 engines, with each engine capable of producing 25,000 or 29,000 pounds of thrust respectively.>
Thought: We've learned that the <https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/f-15e-strike-eagle/|The F-15E Strike Eagle is powered by two Pratt & Whitney F100-PW-220 or 229 engines, with each engine capable of producing 25,000 or 29,000 pounds of thrust respectively.>
Final Answer: The <https://www.cnet.com/pictures/the-16-fastest-combat-planes-in-the-us-air-force/2/|fastest US fighter jet is the F-15E Strike Eagle, with a speed of up to 1,875 miles per hour>. Its specifications include <https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/f-15e-strike-eagle/|two Pratt & Whitney F100-PW-220 or 229 engines, each capable of producing 25,000 or 29,000 pounds of thrust respectively.>
##
Question: {query}\n
Thought: Let's think step-by-step. {transcript}"""
)

web_retriever_prompt = PromptTemplate(
    prompt="""\
Create an informative answer for the given question encased in citatations
Either quote directly or summarize. If you summarize, adopt the tone of the source material. In either case, provide citations for every piece of information you include in the answer.
Always cite your sources, even if they do not directly answer the question.
If the documents do not contain the answer to the question, provide a summary of the relevant information you find instead.
If there is no relevant information, respond with what you know about the topic.
Here are some examples:
<https://example1.com|The Eiffel Tower is located in Paris>.'
Question: Where is the Eiffel Tower located?; Answer: <https://example1.com|The Eiffel Tower is located in Paris>.
<https://example2a.com|Python is a high-level programming language>.'
<https://example2b.com|Python is a scripting language>.'
Question: What is Python?; Answer: <https://example2a.com|Python is a high-level programming language>. <https://example2b.com|Python is a scripting language>

Now, it's your turn.
Documents: {join(documents, delimiter=new_line, pattern=new_line+'<$url|$content>', str_replace={new_line: ' ', '(': '[', ')': ']', '<': '[', '>': ']'})}
Question: {query}
Answer:""",
    output_parser=AnswerParser(reference_pattern=r"<(https?://[^|]+)\|[^>]+>"),
)
