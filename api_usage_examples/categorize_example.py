import re
import json
from collections import Counter
from sllim import chat, system, user, estimate, logger
import logging
from tqdm import tqdm

logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.ERROR)


system_prompt = """\
The prompt categories are:
1. Input Semantics
2. Output Customization
3. Error Identification
4. Prompt Improvement
5. Interaction
6. Context Control
7. None of the above

# Input Semantics definitions:
- "Meta Language Creation pattern":
    When I say X, I mean Y (or would like you to do Y).
    e.g. When I say "3P12NS", I mean generate 3 random passwords of 12 characters including numbers and symbols.

- "Menu Actions pattern":
    Whenever I type: X, you will do Y.
    (Optional, provide additional menu items) Whenever I type Z, you will do Q.
    At the end, you will ask me for the next action.
    e.g. Whenever I type: "feat", you will generate a new feature summary. At the end, you will ask me for the next action.

# Output Customization definitions:
- "Persona pattern": 
    Act as Persona X.
    Perform task Y.
    e.g. Act as Sherlock Holmes. Solve a mystery involving a stolen MacBook.

- "Audience persona pattern":
    Explain X to me.
    Assume that I am Persona Y.
    e.g. Explain the importance of eating vegetables to me. Assume that I am a skeptical child.

- "Output Automator pattern": 
    Whenever you produce an output that has at least one step to take and the following properties (alternatively, always do this).
    Produce an executable artifact of type X that will automate these steps.
    e.g. Whenever you create a meal plan with various ingredients for each meal, generate a Python script that populates a shopping list with the ingredients adjusting quantities based on servings.

- "Visualization Generator pattern":
    Generate an X that I can provide to tool Y to visualize it.
    e.g. When discussing data distributions, generate Python code using matplotlib or seaborn for a histogram representing age distributions in a dataset.

- "Recipe pattern":
    I would like to achieve X.
    I know I need to perform steps A, B, C.
    Provide a complete sequence of steps for me. Fill in any missing steps. (Optional) Identify any unnecessary steps.
    e.g. To become a professional photographer, research and buy a camera, practice photography, and create a portfolio, starting with researching cameras.

- "Template pattern":
    I am going to provide a template for your output.
    X is my placeholder for the content.
    Try to fit the output into the placeholders listed.

- "Tail Generation pattern": 
    At the end, repeat Y and/or ask me for X.
    e.g. At the end of your output, add the disclaimer: "The responses this model generates should not be viewed as entirely accurate or reliable."

# Error Identification definitions:
- "Fact Check List pattern":
    Generate a set of facts that are contained in the output.
    The set of facts should be inserted at POSITION in the output.
    The set of facts should be the fundamental facts that could undermine the veracity of the output if any are incorrect.
    e.g. After generating a news article summary, compile and insert a list of key facts at the end that are crucial to the news story's understanding.

- "Reflection pattern":
    Whenever you generate an answer.
    Explain the reasoning and assumptions behind your answer.
    (Optional) ...so that I can improve my question.
    e.g. When analyzing a stock trend and making a prediction, explain the factors considered and data sources used, and acknowledge potential uncertainties in the prediction.

# Prompt Improvement definitions:
- "Question Refinement pattern":
    Whenever I ask a question, suggest a better version of the question to use instead.
    (Optional) Prompt me if I would like to use the better version instead.
    e.g. When I ask about weight loss, suggest a better version focusing on sustainable practices and ask if I prefer the revised question.

- "Alternative Approaches pattern":
    If there are alternative ways to accomplish task X that I give you, list the best alternate approaches.
    (Optional) Compare/contrast the pros and cons of each approach.
    (Optional) Include the original way that I asked.
    (Optional) Prompt me on which approach I would like to use.
    e.g. For every task I give, list alternate approaches with pros and cons, include the original method, and ask which one I'd like to use.

- "Cognitive Verifier pattern":
    When you are asked a question, follow these rules [RULES].
    Generate a number of additional questions that would help more accurately answer the question.
    Combine the answers to the individual questions to produce the final answer to the overall question.
    e.g. If I ask to evaluate symptoms, ask additional questions to better understand causes and combine answers for a potential diagnosis and suggested treatments.

- "Refusal Breaker pattern":
    Whenever you can't answer a question.
    Explain why you can't answer the question.
    Provide one or more alternative wordings of the question that you could answer.
    e.g. If unable to answer a question about personal data of a public figure, explain why and suggest alternative queries that respect privacy yet provide relevant public information.

# Interaction definitions:
- "Ask for Input pattern":
    Ask me for input X.
    e.g., Generate bullet points for topics I provide and ask which option I prefer for each one.

- "Flipped Interaction pattern":
    I would like you to ask me questions to achieve X.
    You should ask questions until condition Y is met or to achieve this goal (alternatively, forever).
    (Optional) Ask me N questions at a time.
    e.g. To improve my knowledge of world geography, ask me trivia questions until I've answered 50 correctly.

- "Game Play pattern":
    Create a game for me around X OR we are going to play an X game.
    One or more fundamental rules of the game.
    e.g. We will play a language-learning game; you'll provide phrases in a local language, and I will guess the language and meanings, earning points for correct guesses.

- "Infinite Generation pattern":
    Generate output forever, X output(s) at a time.
    (Optional) Here is how to use the input I provide between outputs.
    (Optional) Stop when I ask you to.
    e.g. Keep generating cooking recipes using the ingredients I provide, stopping only when I say, "I'm full." Include all the ingredients I list in each recipe.

# Context Control definitions:
- "Context Manager pattern":
    Within scope X.
    Please consider Y.
    Please ignore Z.
    (Optional) Start over.
    e.g. When discussing novel plots, consider only the main storyline, ignoring subplots or minor characters.

- "Semantic Filter pattern":
    Filter this information to remove X.
    e.g. Filter this news feed to remove any mention of "politics".

Return a JSON object with the following fields:
"category": 1-7, select the category number of the prompt, if one exists, if not, select 7.
"pattern": string, state the specific pattern used in the category, if one exists, if not, state "None of the above".

Example:

Prompt:

\"\"\"
You are a helpful ingredient identifier.
\"\"\"

Response:
{
    "category": 2,
    "pattern": "Persona pattern"
}"""

user_prompt = """Prompt:

\"\"\"
{prompt}
\"\"\""""


def classify_pattern(prompt):
    chat_completion = chat(
        messages=[
            system(system_prompt),
            user(user_prompt.format(prompt=prompt)),
        ],
        model="gpt-4-1106-preview",
        max_tokens=40,
        temperature=0,
        response_format={"type": "json_object"},
    )

    return chat_completion


with open("strings.json") as f:
    strings = json.load(f)

strings = list(filter(lambda x: re.search(r"\s", x), strings))
# print(len(strings))

results = []
for prompt in tqdm(strings):
    r = json.loads(classify_pattern(prompt))
    r["prompt"] = prompt
    results.append(r)

# print(estimate([system(system_prompt)]))
# print(estimate([system(system_prompt)])["cost"] * len(strings[:100]))

with open("classification.json", "w") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(
    sorted(
        Counter(list(map(lambda x: x["category"], results))).items(),
        key=lambda x: x[0],
    )
)
