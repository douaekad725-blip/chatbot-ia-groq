import requests
import os
import time
from dotenv import load_dotenv
from colorama import Fore, Style, init

init()

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print(Fore.RED + "❌ Erreur: Clé API non trouvée dans .env" + Style.RESET_ALL)
    exit()


url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


conversation = [
    {"role": "system", "content": "Tu es un assistant intelligent, créatif et utile."}
]

print(Fore.GREEN + "🤖 Bot: Salut! Je suis prêt. Tape 'exit' pour quitter." + Style.RESET_ALL)

while True:
    
    user_input = input(Fore.CYAN + "👤 Toi: " + Style.RESET_ALL)
    
    if user_input.lower() == "exit":
        print(Fore.YELLOW + "👋 Bot: Au revoir! Bonne journée!" + Style.RESET_ALL)
        break
    
    if not user_input.strip():
        continue

    
    conversation.append({"role": "user", "content": user_input})


    data = {
        "model": "llama-3.1-8b-instant",
        "messages": conversation
    }

    try:
       
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        
        bot_reply = response.json()["choices"][0]["message"]["content"]
        
        
        print(Fore.GREEN + "🤖 Bot: " + Style.RESET_ALL, end="", flush=True)
        for char in bot_reply:
            print(char, end="", flush=True)
            time.sleep(0.02) 
        print("\n") 
        
        
        conversation.append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        print(Fore.RED + f"❌ Erreur: {e}" + Style.RESET_ALL)
