import openai
import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub

# Tools
from tool.problem import merge_pickles, filter_negative_reviews

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=openai_api_key,
    temperature=0)

tools = [merge_pickles, filter_negative_reviews]

# Prompt - 원하면 추가 작성 가능
prompt = ChatPromptTemplate.from_messages([
    ("system",
"""
You are a data analysis assistant capable of using tools when helpful.

Context:
- There are datasets split into multiple pickle files.
- Sometimes, these files must be merged into a single dataset before analysis.
- Some tools allow filtering negative reviews for deeper insights.

Your job:
- Understand the user request.
- If merging is required, use `merge_pickles`.
- If reviewing or analyzing customer reviews, consider using `filter_negative_reviews`.
- After completing necessary tool calls, produce a final written report summarizing the insights.

Report Format Rules:
- The final report MUST be written in structured paragraphs.
- Each section MUST follow this format:

  ## 부제(Section Title)
  내용(Content in paragraphs)

- No bullet lists unless necessary.
- The overall report must include:
  - 주요 불만 원인(complaint reasons)
  - 가장 많은 age_group
  - 가장 많은 product_category
  - 분석을 기반으로 한 problem summary

Guidelines:
- You MAY call tools if useful. Tools are optional but recommended.
- Do NOT ask the user for tool-specific input (like file paths).
- NEVER include tool call results in the final report until tools have completed.
- Final answer must be a natural language report.
- Think step-by-step and use tools wisely.
"""

    ),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])


agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":

    merge_result = agent_executor.invoke({"input": "분리된 pickle 파일들을 하나로 합쳐주세요."})
    filter_result = agent_executor.invoke({"input": "부정적인 리뷰만 필터링 하고 리포트를 작성해주세요."})

    # 2) Agent 출력 텍스트만 추출
    report_text = filter_result.get("output", "")

    # 3) docx로 저장
    from styled_docx import create_styled_report
    create_styled_report(report_text, "analysis_report.docx")
