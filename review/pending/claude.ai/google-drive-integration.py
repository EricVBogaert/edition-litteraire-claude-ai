import os
import io
import tempfile
from typing import List, Dict, Any, Optional

# Google Drive API
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# Claude API
import anthropic

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')


class DocumentAnalyzer:
    """
    Classe pour analyser des documents Google Drive avec Claude
    """
    
    def __init__(self, claude_api_key: str, service_account_file: str):
        # Initialisation du client Claude
        self.claude = anthropic.Anthropic(api_key=claude_api_key)
        
        # Initialisation de l'API Google Drive
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)
        self.drive_service = build('drive', 'v3', credentials=credentials)
    
    def download_document(self, file_id: str) -> tuple:
        """
        Télécharge un document depuis Google Drive
        Retourne: (nom du fichier, contenu du fichier)
        """
        # Récupérer les métadonnées du fichier
        file_metadata = self.drive_service.files().get(fileId=file_id).execute()
        file_name = file_metadata['name']
        mime_type = file_metadata['mimeType']
        
        # Télécharger le contenu du fichier
        request = self.drive_service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Téléchargement {int(status.progress() * 100)}%.")
        
        file_content.seek(0)
        
        # Selon le type de fichier, extraire le texte
        if mime_type == 'application/pdf':
            text_content = self._extract_text_from_pdf(file_content)
        elif mime_type in ['text/plain', 'text/csv']:
            text_content = file_content.read().decode('utf-8')
        elif mime_type in ['application/vnd.google-apps.document', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            # Pour les documents Google Docs ou Word, exporter en texte
            text_content = self._export_as_text(file_id)
        else:
            raise ValueError(f"Type de fichier non pris en charge: {mime_type}")
        
        return file_name, text_content
    
    def _export_as_text(self, file_id: str) -> str:
        """
        Exporte un document Google Docs en texte
        """
        request = self.drive_service.files().export_media(
            fileId=file_id, mimeType='text/plain')
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_content.seek(0)
        return file_content.read().decode('utf-8')
    
    def _extract_text_from_pdf(self, pdf_content: io.BytesIO) -> str:
        """
        Extrait le texte d'un fichier PDF
        """
        # Utilisation de PyPDF2 pour extraire le texte
        import PyPDF2
        
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        
        return text
    
    def analyze_document(self, file_id: str, analysis_prompt: str, 
                        model: str = "claude-3-7-sonnet-20250219") -> Dict[str, Any]:
        """
        Analyse un document Google Drive avec Claude
        
        Args:
            file_id: ID du fichier Google Drive
            analysis_prompt: Instructions pour l'analyse
            model: Modèle Claude à utiliser
            
        Returns:
            Dictionnaire contenant l'analyse et les métadonnées
        """
        try:
            # Télécharger le document
            file_name, text_content = self.download_document(file_id)
            
            # Limiter la taille du contenu si nécessaire (éviter les dépassements de contexte)
            if len(text_content) > 100000:  # ~25K tokens
                text_content = text_content[:100000] + "\n...[Contenu tronqué]..."
            
            # Construire le prompt complet
            full_prompt = f"""Voici le contenu du document '{file_name}':

---BEGIN DOCUMENT---
{text_content}
---END DOCUMENT---

{analysis_prompt}
"""
            
            # Appeler Claude pour l'analyse
            response = self.claude.messages.create(
                model=model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            # Extraire la réponse
            analysis = response.content[0].text
            
            # Retourner les résultats avec métadonnées
            return {
                "file_name": file_name,
                "file_id": file_id,
                "analysis": analysis,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                },
                "model": model
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "file_id": file_id,
                "status": "error"
            }
    
    def batch_analyze_documents(self, file_ids: List[str], analysis_prompt: str, 
                              model: str = "claude-3-7-sonnet-20250219") -> List[Dict[str, Any]]:
        """
        Analyse un lot de documents Google Drive
        """
        results = []
        
        for file_id in file_ids:
            try:
                print(f"Analyse du document {file_id}...")
                result = self.analyze_document(file_id, analysis_prompt, model)
                results.append(result)
            except Exception as e:
                results.append({
                    "file_id": file_id,
                    "error": str(e),
                    "status": "error"
                })
        
        return results


# Exemple d'utilisation
def demo_document_analyzer():
    analyzer = DocumentAnalyzer(
        claude_api_key=CLAUDE_API_KEY,
        service_account_file=SERVICE_ACCOUNT_FILE
    )
    
    # ID de fichier Google Drive à analyser
    file_id = "votre_id_de_fichier_google_drive"
    
    # Prompt d'analyse
    analysis_prompt = """
    Fais une analyse complète de ce document en fournissant:
    1. Un résumé général (max 3 paragraphes)
    2. Les points clés et idées principales
    3. Une évaluation critique des arguments présentés
    4. Des recommandations pour approfondir le sujet
    """
    
    # Exécuter l'analyse
    result = analyzer.analyze_document(file_id, analysis_prompt)
    
    # Afficher les résultats
    print(f"Analyse du document: {result['file_name']}")
    print(f"Tokens utilisés: {result['tokens']['total']}")
    print("\nANALYSE:")
    print(result['analysis'])
    
    return result


if __name__ == "__main__":
    demo_document_analyzer()
