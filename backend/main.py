import os

from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY is missing from .env")


# ============================================================
# CLIENTS
# ============================================================

gemini = genai.Client(
    api_key=gemini_api_key
)

tavily = TavilyClient(
    api_key=tavily_api_key
)


# ============================================================
# SEARCH FUNCTION
# ============================================================

def search_web(query):
    print(f"\nSearching the web for: {query}\n")

    results = tavily.search(
        query=query,
        max_results=5
    )

    return results["results"]


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(question):

    # --------------------------------------------------------
    # 1. Search the internet
    # --------------------------------------------------------

    search_results = search_web(question)

    # --------------------------------------------------------
    # 2. Convert search results into context
    # --------------------------------------------------------

    web_context = ""

    for i, result in enumerate(search_results, start=1):

        web_context += f"""
SOURCE {i}

Title:
{result["title"]}

URL:
{result["url"]}

Content:
{result["content"]}

----------------------------------------
"""

    # --------------------------------------------------------
    # 3. Give the web information to Gemini
    # --------------------------------------------------------

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using the web search
results provided below.

Important rules:

1. Prefer information from the search results.
2. Do not invent facts that are not supported by the sources.
3. If the sources disagree, explain the disagreement.
4. Include the source URLs at the end of your answer.
5. If the search results do not contain enough information,
   say so.

WEB SEARCH RESULTS:

{web_context}


USER QUESTION:

{question}
"""

    response = gemini.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ============================================================
# CHAT LOOP
# ============================================================

print("Gemini + Web Search")
print("Type 'exit' to quit.\n")


while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    try:

        answer = ask_gemini(question)

        print("\nGemini:")
        print(answer)
        print()

    except Exception as e:

        print("\nERROR:")
        print(e)