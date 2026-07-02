from google import genai
import db_manager

# --- 1. Setup Gemini API ---
API_KEY = "AIzaSyALY2KWIfnsTZ3ckA76B7b_uiIKlr56smQ" 
client = genai.Client(api_key=API_KEY)

# --- 2. Smart Task Planner ---

def generate_task_plan(title, description):
    """
    Asks the AI to suggest a required plan and checklist 
    based specifically on the task title and description.
    """
    if not API_KEY.startswith("AIza"):
        return "Please add your valid Gemini API Key to line 6."
        
    prompt = f"""
    You are a productivity assistant. I need to complete the following task:
    Task Title: '{title}'
    Task Description: '{description}'
    
    Please suggest the required plan to accomplish this task. 
    Format your response as a clear, practical, step-by-step checklist.
    
    CRITICAL FORMATTING RULES:
    1. DO NOT use any Markdown formatting whatsoever (no asterisks **, no hashes ###, no backticks).
    2. Provide PLAIN TEXT only.
    3. Use all CAPITAL LETTERS for Phase or Category headings.
    4. Use standard numbers (1., 2., 3.) for main steps.
    5. Use standard dashes (-) for sub-steps or checklist items.
    6. Leave a clear blank line between different phases to make it easy to read on a screen.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: Could not generate task plan. ({e})"

# --- 3. Test Block ---
if __name__ == "__main__":
    print("--- Testing AI Task Planner ---")
    test_title = "College AI Project"
    test_desc = "Need to build the frontend GUI and connect it to the MySQL database."
    print(generate_task_plan(test_title, test_desc))
