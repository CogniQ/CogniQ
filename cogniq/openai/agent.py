from .config import Config

from haystack.nodes import PromptNode, PromptTemplate

# For the pipeline to work, you'd need to import the Reader, Retriever, and DocumentStore
# This example skips the pipeline configuration steps
from haystack.agents import Agent
from haystack.agents.base import ToolsManager
from haystack.nodes import PromptNode, PromptTemplate

from .web_qa_tool import web_qa_tool


few_shot_prompt = """
You have the ability to answer complex questions using tools like Search and Ask. 
Use targeted questions for accurate results. 
Each step involves selecting a tool, creating an input, and receiving observations. Cite your sources, and compose a final answer with key points.
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
Question: Who is asdfqwer?
Thought: This question appears to be incomplete and requires more context or information to provide an accurate answer. Please provide additional details or rephrase the question.
Tool: Ask
Tool Input: This question appears to be incomplete and requires more context or information to provide an accurate answer. Please provide additional details or rephrase the question.
Observation: This question appears to be unclear and requires more context or information to provide an accurate answer. Please provide additional details or rephrase the question.
Thought: I don't have enough information to answer this question. I'll respond that more context or rephrasing is needed.
Final Answer: More context or rephrasing is needed to answer this question.
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
Thought:
"""
few_shot_agent_template = PromptTemplate("few-shot-react", prompt_text=few_shot_prompt)

prompt_node = PromptNode(
    "gpt-3.5-turbo",
    api_key=Config["OPENAI_API_KEY"],
    max_length=Config["OPENAI_MAX_TOKENS_RESPONSE"],
    stop_words=["Observation:"],
)

agent = Agent(
    prompt_node=prompt_node,
    prompt_template=few_shot_agent_template,
    tools_manager=ToolsManager([web_qa_tool]),
)
