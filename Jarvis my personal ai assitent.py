# ============================================================
#                    J.A.R.V.I.S. 6.0
#              YOUR PERSONAL AI ASSISTANT
#                   ANDROID + PYTHON
# ============================================================

import os
import ast
import math
import operator
import datetime
import subprocess
import shutil

# -------------------- SETTINGS --------------------

ASSISTANT_NAME = "JARVIS"
VERSION = "6.0"

MODEL = os.getenv("JARVIS_MODEL", "gpt-5.5")

NOTES_FILE = "jarvis_notes.txt"
MAX_HISTORY = 12

conversation = []
client = None

# -------------------- AI LIBRARY --------------------

try:
    from openai import OpenAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# -------------------- CONNECT AI --------------------

def connect_ai():

    global client

    if not AI_AVAILABLE:
        print("Install: pip install openai")
        return False

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("API key not configured.")
        return False

    try:
        client = OpenAI(api_key=api_key)
        speak("Artificial intelligence connected.")
        return True

    except Exception as error:
        client = None
        print("Connection error:", type(error).__name__)
        return False


# -------------------- VOICE OUTPUT --------------------

def speak(message):

    message = str(message)

    print("\n" + ASSISTANT_NAME + ":")
    print(message)

    if shutil.which("termux-tts-speak"):

        try:
            subprocess.run(
                ["termux-tts-speak", message],
                timeout=30,
                check=False
            )
        except Exception:
            pass


# -------------------- VOICE INPUT --------------------

def listen():

    if not shutil.which("termux-speech-to-text"):
        speak("Voice input unavailable. Please type.")
        return input("YOU: ").strip()

    try:

        speak("I am listening.")

        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        command = result.stdout.strip()

        if command:
            print("YOU:", command)
            return command.lower()

        speak("Please repeat your command.")
        return ""

    except Exception:
        speak("Voice recognition failed.")
        return ""


# -------------------- AI BRAIN --------------------

def ask_ai(question):

    global conversation

    if client is None:
        return "My AI brain is disconnected. Connect your API first."

    conversation.append({
        "role": "user",
        "content": question
    })

    try:

        response = client.responses.create(

            model=MODEL,

            instructions=(
                "Your name is JARVIS. "
                "You are a helpful personal AI assistant. "
                "Speak in simple Hindi or English depending "
                "on the user's language. "
                "Explain educational topics clearly. "
                "Be friendly, intelligent and safe."
            ),

            input=conversation[-MAX_HISTORY:],

            max_output_tokens=700
        )

        answer = response.output_text or "No response received."

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        conversation = conversation[-MAX_HISTORY:]

        return answer

    except Exception as error:

        conversation.pop()

        return "AI error: " + type(error).__name__


# -------------------- SAFE CALCULATOR --------------------

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv
}


def calculate(expression):

    def solve(node):

        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):

            if type(node.value) in (int, float):
                return node.value

        if isinstance(node, ast.UnaryOp):

            value = solve(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        if isinstance(node, ast.BinOp):

            if type(node.op) not in OPERATIONS:
                raise ValueError()

            left = solve(node.left)
            right = solve(node.right)

            if abs(left) > 10**50 or abs(right) > 10**50:
                raise ValueError()

            if isinstance(node.op, ast.Pow):
                if abs(right) > 100 or abs(left) > 10**6:
                    raise ValueError()

            result = OPERATIONS[type(node.op)](left, right)

            if not math.isfinite(float(result)):
                raise ValueError()

            if abs(result) > 10**50:
                raise ValueError()

            return result

        raise ValueError()

    try:

        if len(expression) > 150:
            return "Expression too long"

        tree = ast.parse(expression, mode="eval")

        if len(list(ast.walk(tree))) > 50:
            return "Expression too complex"

        return solve(tree)

    except Exception:
        return "Invalid calculation"


# -------------------- NOTES SYSTEM --------------------

def save_note():

    note = input("Write your note: ").strip()

    if not note:
        speak("Empty note not saved.")
        return

    try:

        with open(NOTES_FILE, "a", encoding="utf-8") as file:

            file.write(
                "\n" +
                datetime.datetime.now().strftime(
                    "%d-%m-%Y %I:%M %p"
                ) +
                "\n" + note + "\n"
            )

        speak("Your note has been saved.")

    except OSError:
        speak("Could not save note.")


def read_notes():

    if not os.path.exists(NOTES_FILE):
        speak("You have no saved notes.")
        return

    try:

        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            notes = file.read()

        speak("Here are your saved notes.")
        print(notes)

    except OSError:
        speak("Could not read notes.")


# -------------------- DATE AND TIME --------------------

def show_time():

    now = datetime.datetime.now()

    speak("The current time is " + now.strftime("%I:%M %p"))


def show_date():

    today = datetime.date.today()

    speak("Today's date is " + today.strftime("%d %B %Y"))


# -------------------- COMMAND SYSTEM --------------------

def process_command(command):

    command = command.lower().strip()

    if not command:
        return True

    if command in ["exit", "quit", "shutdown", "goodbye"]:

        speak("Goodbye! JARVIS shutting down.")
        return False

    elif command in ["hello", "hi", "hey"]:

        speak("Hello! How may I help you?")

    elif "your name" in command:

        speak("I am JARVIS, your personal AI assistant.")

    elif "time" in command:

        show_time()

    elif "date" in command:

        show_date()

    elif command in ["calculator", "calculate"]:

        expression = input("Enter calculation: ")
        speak("Result: " + str(calculate(expression)))

    elif command == "save note":

        save_note()

    elif command == "read notes":

        read_notes()

    elif command == "clear chat":

        conversation.clear()
        speak("Conversation memory cleared.")

    elif command == "connect ai":

        connect_ai()

    elif command == "help":

        speak(
            "I can answer questions, calculate, save notes, "
            "read notes, tell date and time, and use voice."
        )

    else:

        speak(ask_ai(command))

    return True


# -------------------- INTERFACE --------------------

def display_interface():

    print("\n")
    print("=" * 50)
    print("             J.A.R.V.I.S. " + VERSION)
    print("          PERSONAL AI ASSISTANT")
    print("=" * 50)

    print(" [1] Voice Assistant")
    print(" [2] Type a Command")
    print(" [3] Ask AI")
    print(" [4] Calculator")
    print(" [5] Save Notes")
    print(" [6] Read Notes")
    print(" [7] Date and Time")
    print(" [8] Connect AI")
    print(" [9] Clear Chat Memory")
    print(" [0] Exit")

    print("=" * 50)


# -------------------- MAIN PROGRAM --------------------

def start_jarvis():

    speak("Welcome! JARVIS version 6.0 is starting.")

    if AI_AVAILABLE:
        connect_ai()
    else:
        speak("AI library missing. Basic mode activated.")

    while True:

        display_interface()

        choice = input("\nSelect option: ").strip()

        if choice == "1":

            if not process_command(listen()):
                break

        elif choice == "2":

            if not process_command(input("YOU: ")):
                break

        elif choice == "3":

            question = input("Ask JARVIS AI: ")
            speak(ask_ai(question))

        elif choice == "4":

            expression = input("Enter calculation: ")
            speak("Result: " + str(calculate(expression)))

        elif choice == "5":

            save_note()

        elif choice == "6":

            read_notes()

        elif choice == "7":

            show_date()
            show_time()

        elif choice == "8":

            connect_ai()

        elif choice == "9":

            conversation.clear()
            speak("Chat memory cleared.")

        elif choice == "0":

            speak("Goodbye! See you again.")
            break

        else:

            speak("Invalid option.")


# -------------------- START JARVIS --------------------

if __name__ == "__main__":

    try:
        start_jarvis()

    except KeyboardInterrupt:
        print("\nJARVIS stopped.")