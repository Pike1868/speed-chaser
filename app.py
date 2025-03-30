import argparse
import os
import textwrap
from config import SYSTEM_PROMPT, REFS_FOLDER, OPENROUTER_API_KEY, DEFAULT_MODEL, CONTEXTS
from utils.pdf_parser import extract_text_from_pdf
# Removed: from adapters import zohodesk_adapter
from retriever import retrieve, load_index_and_metadata


def call_openrouter(prompt):
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "Error in API response: " + str(data)


def call_openrouter_with_history(messages):
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "Error in API response: " + str(data)


def continuous_chat_loop(conversation_history):
    """
    Each user input triggers:
    - Vector retrieval of relevant docs (if index is available)
    - Combining retrieved docs with the user message
    - Passing everything to the model
    """
    wrapper = textwrap.TextWrapper(width=80)

    # Attempt to load FAISS at the start.
    # If not found, user can still chat but no context retrieval.
    index_available = True
    try:
        _idx, _meta = load_index_and_metadata()
    except FileNotFoundError:
        index_available = False
        print("\nSpeedChaser AI : No vector index found. I'll proceed without doc retrieval.")

    while True:
        prompt = input("\nYou: ")
        if prompt.lower() == "exit":
            break

        # If an index is available, retrieve relevant docs
        relevant_docs_text = ""
        if index_available:
            docs = retrieve(prompt, top_k=3)
            for doc in docs:
                relevant_docs_text += f"[{doc['filename']} chunk]:\n{doc['content']}\n\n"

        # Build the final prompt with retrieved doc context
        if relevant_docs_text:
            system_context = f"Relevant local context:\n{relevant_docs_text}"
        else:
            system_context = ""

        conversation_history_with_context = conversation_history.copy()
        if system_context:
            conversation_history_with_context.append({"role": "system", "content": system_context})

        conversation_history_with_context.append({"role": "user", "content": prompt})

        # Call OpenRouter with the updated conversation
        response = call_openrouter_with_history(conversation_history_with_context)

        # Print result
        formatted_response = wrapper.fill(response)
        print("\nSpeedChaser AI :\n", formatted_response)

        # Update the conversation history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response})


def guided_mode(context=None):
    prompt_context = SYSTEM_PROMPT
    if context and context in CONTEXTS:
        prompt_context = CONTEXTS[context]["prompt"]

    print("\nSpeedChaser AI :", "Welcome to Speed Chaser Guided Mode!")
    if context:
        print(f"\nSpeedChaser AI : Current context set to '{context}'")

    print("\nSpeedChaser AI :", "Entering continuous chat mode (type 'exit' to quit).")
    conversation_history = [{"role": "system", "content": prompt_context}]
    continuous_chat_loop(conversation_history)


def run_ingestion(path):
    import subprocess
    print(f"\nSpeedChaser AI : Running ingestion on path: {path}\n")
    try:
        subprocess.run(["python", "ingest.py", "--path", path], check=True)
        print("\nSpeedChaser AI : Ingestion complete.")
    except subprocess.CalledProcessError as e:
        print("\nSpeedChaser AI : Ingestion failed:", str(e))


def main():
    parser = argparse.ArgumentParser(description="Speed Chaser AI Assistant")
    parser.add_argument("--prompt", type=str, help="Submit a freeform prompt")
    parser.add_argument("--file", type=str, help="File from refs folder to process")
    parser.add_argument("--guided", action="store_true", help="Launch guided interactive mode")
    parser.add_argument("--generate-docs", action="store_true", help="Generate configuration documentation")
    parser.add_argument("--context", type=str, help="Context mode to use (e.g., nextread, work-support)")
    parser.add_argument("--ingest", action="store_true", help="Ingest files for context-aware responses")
    parser.add_argument("--path", type=str, default=".", help="Path to ingest if using --ingest")
    args = parser.parse_args()

    # Prompt user if no vector index
    if not os.path.exists("vectorstore/index.faiss"):
        print("\nSpeedChaser AI : I notice you don't have an index built yet. Would you like to ingest your files now? (y/n)")
        choice = input("> ").strip().lower()
        if choice == "y":
            run_ingestion(args.path)

    if args.ingest:
        run_ingestion(args.path)

    elif args.guided:
        guided_mode(context=args.context)

    elif args.generate_docs:
        doc = f"# Speed Chaser Configuration\n\n"
        doc += f"**System Prompt:** {SYSTEM_PROMPT}\n\n"
        doc += f"**Reference Folder:** {REFS_FOLDER}\n\n"
        doc += "Add more configuration details as needed."
        print("\nSpeedChaser AI :", doc)
        os.makedirs("docs", exist_ok=True)
        with open("docs/current_config.md", "w", encoding="utf-8") as f:
            f.write(doc)
        print("\nSpeedChaser AI :", "Documentation saved to docs/current_config.md")

    elif args.prompt:
        response = call_openrouter(args.prompt)
        print("\nSpeedChaser AI : Response:")
        print("\nSpeedChaser AI :", response)

    elif args.file:
        file_path = os.path.join(REFS_FOLDER, args.file)
        if not os.path.exists(file_path):
            print("\nSpeedChaser AI :", "File not found!")
            return
        if args.file.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        full_prompt = f"File content: {text}\nTask: {args.task if args.task else 'Process this file.'}"
        response = call_openrouter(full_prompt)
        print("\nSpeedChaser AI :", "Response:")
        print("\nSpeedChaser AI :", response)

    else:
        print("\nSpeedChaser AI :", "No valid command provided. Use --help for usage details.")


if __name__ == "__main__":
    main()
