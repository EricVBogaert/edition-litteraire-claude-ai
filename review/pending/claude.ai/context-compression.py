import anthropic
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContextCompressor:
    """
    Classe pour compresser le contexte avant les appels API à Claude
    """
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def count_tokens(self, text):
        """Estime le nombre de tokens dans un texte"""
        return self.client.count_tokens(text)
    
    def summarize_conversation(self, messages, max_summary_tokens=500):
        """
        Utilise Claude pour résumer la conversation jusqu'à présent
        """
        # Formatage de la conversation pour le résumé
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in messages
        ])
        
        summary_prompt = f"""Voici une conversation entre un utilisateur et un assistant IA:

{conversation_text}

Résume cette conversation en conservant TOUTES les informations importantes, 
les faits, les préférences exprimées, et les décisions prises.
Sois concis mais complet, en te limitant à environ {max_summary_tokens} tokens.
"""
        
        # Appel à Claude pour résumer
        response = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=max_summary_tokens,
            messages=[
                {"role": "user", "content": summary_prompt}
            ]
        )
        
        summary = response.content[0].text
        return {
            "role": "system", 
            "content": f"Résumé de la conversation précédente: {summary}"
        }
    
    def relevance_filter(self, messages, current_query, threshold=0.2):
        """
        Filtre les messages par pertinence avec la requête actuelle
        en utilisant la similarité cosinus
        """
        if len(messages) <= 2:  # Conserver au moins les 2 derniers messages
            return messages
            
        # Transformer tous les messages en vecteurs TF-IDF
        message_texts = [msg["content"] for msg in messages]
        message_texts.append(current_query)
        
        # Fit et transform sur tous les textes
        try:
            tfidf_matrix = self.vectorizer.fit_transform(message_texts)
            
            # Le dernier vecteur est la requête actuelle
            query_vector = tfidf_matrix[-1]
            
            # Calculer les similarités
            similarities = cosine_similarity(query_vector, tfidf_matrix[:-1])[0]
            
            # Sélectionner les messages au-dessus du seuil de pertinence
            filtered_indices = [i for i, sim in enumerate(similarities) if sim > threshold]
            
            # Toujours inclure les 2 derniers messages pour la continuité
            if len(filtered_indices) < 2:
                filtered_indices.extend([len(messages)-2, len(messages)-1])
                filtered_indices = list(set(filtered_indices))  # Dédupliquer
                
            # Trier pour maintenir l'ordre chronologique
            filtered_indices.sort()
            
            # Retourner les messages filtrés
            filtered_messages = [messages[i] for i in filtered_indices]
            return filtered_messages
            
        except:
            # Fallback en cas d'erreur
            return messages[-5:]  # Retourner les 5 derniers messages par défaut
    
    def sliding_window(self, messages, window_size=5):
        """
        Applique une fenêtre glissante pour ne conserver que 
        les derniers messages du contexte
        """
        if len(messages) <= window_size:
            return messages
        else:
            # Toujours conserver le premier message (instructions initiales)
            return [messages[0]] + messages[-(window_size-1):]
    
    def compress_by_strategy(self, messages, current_query, 
                            target_token_limit=5000, strategy="hybrid"):
        """
        Compresse le contexte en utilisant différentes stratégies
        pour rester sous une limite de tokens
        
        Stratégies:
        - "sliding": fenêtre glissante simple
        - "relevance": filtrage par pertinence
        - "summary": résumé de la conversation précédente
        - "hybrid": combinaison des approches
        """
        # Estimer les tokens actuels
        current_tokens = sum(self.count_tokens(msg["content"]) for msg in messages)
        current_tokens += self.count_tokens(current_query)
        
        # Si déjà sous la limite, pas besoin de compression
        if current_tokens <= target_token_limit:
            return messages
        
        # Stratégie de fenêtre glissante
        if strategy == "sliding":
            # Calculer la taille de fenêtre possible
            tokens_per_message = current_tokens / len(messages)
            possible_window = int(target_token_limit / tokens_per_message)
            return self.sliding_window(messages, window_size=max(3, possible_window))
        
        # Stratégie de filtrage par pertinence
        elif strategy == "relevance":
            return self.relevance_filter(messages, current_query)
        
        # Stratégie de résumé
        elif strategy == "summary":
            # Résumer tous les messages sauf les 2 derniers
            if len(messages) <= 2:
                return messages
                
            summary_msg = self.summarize_conversation(messages[:-2])
            return [summary_msg] + messages[-2:]
        
        # Stratégie hybride (la plus efficace en général)
        elif strategy == "hybrid":
            # Si le contexte est petit, utiliser sliding window
            if len(messages) < 10:
                return self.sliding_window(messages)
            
            # Pour un contexte moyen, filtrer par pertinence
            elif len(messages) < 20:
                return self.relevance_filter(messages, current_query)
                
            # Pour un contexte long, combiner résumé et pertinence
            else:
                # Résumer l'historique ancien
                old_messages = messages[:-10]
                recent_messages = messages[-10:]
                
                summary_msg = self.summarize_conversation(old_messages)
                
                # Filtrer les messages récents par pertinence
                filtered_recent = self.relevance_filter(recent_messages, current_query)
                
                return [summary_msg] + filtered_recent
        
        # Par défaut, retourner les 5 derniers messages
        return messages[-5:]

    def optimized_api_call(self, messages, current_query, 
                          max_tokens=1000, target_context_tokens=5000):
        """
        Optimise l'appel API en compressant le contexte intelligemment
        """
        # Compresser le contexte
        compressed_messages = self.compress_by_strategy(
            messages, current_query, target_context_tokens, "hybrid"
        )
        
        # Ajouter la requête actuelle
        compressed_messages.append({"role": "user", "content": current_query})
        
        # Faire l'appel API avec contexte optimisé
        response = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=max_tokens,
            messages=compressed_messages
        )
        
        return response
