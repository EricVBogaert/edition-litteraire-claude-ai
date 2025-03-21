import anthropic

# Initialisation du client
client = anthropic.Anthropic(api_key="votre_clé_api")

# Comptage approximatif des tokens (méthode intégrée d'Anthropic)
def estimate_tokens(text):
    return client.count_tokens(text)

# Exemple d'utilisation avec gestion des tokens
def generate_with_token_management(prompt, max_tokens_to_use=1000):
    # Estimation des tokens d'entrée
    prompt_tokens = estimate_tokens(prompt)
    
    # Calcul des tokens restants pour la réponse
    output_tokens = max_tokens_to_use - prompt_tokens
    
    if output_tokens < 100:
        return "Prompt trop long, veuillez le réduire"
    
    # Génération de la réponse avec limitation des tokens
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",  # Modèle actuel 
        max_tokens=output_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Retourner la réponse et les statistiques d'utilisation
    return {
        "response": message.content[0].text,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": estimate_tokens(message.content[0].text),
            "total_tokens": prompt_tokens + estimate_tokens(message.content[0].text)
        }
    }
