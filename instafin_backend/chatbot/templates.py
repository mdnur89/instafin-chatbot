from typing import Dict, List
import random
from string import Template

class ResponseTemplateManager:
    """Manages response templates for the chatbot"""
    
    @staticmethod
    async def get_template(intent) -> str:
        """Get a random response template for the given intent"""
        if not intent.response_templates:
            return "I understand, but I'm not sure how to respond to that."
        
        return random.choice(intent.response_templates)
    
    @staticmethod
    async def fill_template(template: str, entities: Dict) -> str:
        """Fill template with entity values"""
        try:
            # Convert entities to strings to avoid type issues
            safe_entities = {k: str(v) for k, v in entities.items()}
            return Template(template).safe_substitute(safe_entities)
        except KeyError as e:
            # If template has placeholders that we don't have values for
            return "I understand, but I'm missing some information to respond properly."
        except Exception as e:
            # Fallback for any other template processing errors
            return "I understand, but I'm having trouble forming a response."

    @staticmethod
    def get_default_templates() -> Dict[str, List[str]]:
        """Get default response templates for common intents"""
        return {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What can I assist you with?",
                "Welcome! How may I help you?"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "Thanks for chatting! Take care!",
                "Bye! Feel free to reach out if you need anything else!"
            ],
            "thanks": [
                "You're welcome!",
                "Happy to help!",
                "Anytime! Let me know if you need anything else!"
            ],
            "loan_inquiry": [
                "I see you're interested in a ${loan_type} loan for ${amount}. Let me help you with that.",
                "For a ${loan_type} loan of ${amount}, here are the details you need:",
                "I can help you with your ${loan_type} loan request for ${amount}."
            ],
            "balance_inquiry": [
                "Your current balance is ${balance}.",
                "The balance in your account is ${balance}.",
                "You have ${balance} in your account."
            ],
            "payment_status": [
                "Your next payment of ${amount} is due on ${due_date}.",
                "You have a payment of ${amount} scheduled for ${due_date}.",
                "The upcoming payment is ${amount}, due on ${due_date}."
            ],
            "fallback": [
                "I'm not quite sure I understand. Could you please rephrase that?",
                "I didn't catch that. Can you say it differently?",
                "I'm having trouble understanding. Could you try again?"
            ],
            "escalation": [
                "Let me connect you with a human agent who can better assist you.",
                "I'll transfer you to one of our customer service representatives.",
                "A human agent will be with you shortly to help with your request."
            ]
        } 