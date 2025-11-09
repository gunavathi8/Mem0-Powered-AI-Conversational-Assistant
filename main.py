# Improved version of main.py (CLI)
# Added: Logging, better input handling.

from workflow import run_conversation
from config import DEFAULT_USER_ID
from memory_manager import close_memory
import logging
import atexit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register shutdown hook
atexit.register(close_memory)

def main():
    print("Welcome to Chat with me :) How are you doing buddy?")
    mem0_user_id = DEFAULT_USER_ID

    try:
        while True:
            user_input = input("🙎 You: ").strip()
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Thanks for chatting with me. Bye!")
                break
            if not user_input:
                continue
            response = run_conversation(user_input, mem0_user_id)
            print(f"🤖 Assistant: {response}")
    except KeyboardInterrupt:
        print("\nInterrupted. Bye!")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        close_memory()
        print("✅ Memory closed cleanly")

if __name__ == "__main__":
    main()