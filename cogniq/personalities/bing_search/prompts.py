agent_prompt = """\
You have the ability to answer complex questions using tools like Search.
Use targeted questions for accurate results. 
Each step involves selecting a tool, creating an input, and receiving observations.
Compose a final answer with key points, ensuring that you cite your sources.
You have access to the following tools:

Search: useful for when you need to Google questions.

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
Question: {query}
Thought:"""

web_retriever_prompt = """\
Create an informative answer (approximately 100 words) for a given question encased in citatations
Either quote directly or summarize. If you summarize, adopt the tone of the source material. If either case, provide citations for every piece of information you include in the answer.
Always cite your sources, even if they do not directly answer the question.
If the documents do not contain the answer to the question, provide a summary of the relevant information you find instead.
Here are some examples:
<https://example1.com|The Eiffel Tower is located in Paris>.'
Question: Where is the Eiffel Tower located?; Answer: <https://example1.com|The Eiffel Tower is located in Paris>.
<https://example2a.com|Python is a high-level programming language>.'
<https://example2b.com|Python is a scripting language>.'
Question: What is Python?; Answer: <https://example2a.com|Python is a high-level programming language>. <https://example2b.com|Python is a scripting language>
Now, it's your turn.
{join(documents, delimiter=new_line, pattern=new_line+'<$url|$content>', str_replace={new_line: ' ', '[': '(', ']': ')'})}
Question: {query}; Answer:"""
