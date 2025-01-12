from anthropic import Anthropic

class MarketplaceAIAgent:
    def __init__(self, anthropic_api_key):
        self.client = Anthropic(api_key=anthropic_api_key)
        self.conversation_stages = {
            'questions': 'User is asking questions about the product',
            'negotiation': 'User is negotiating the price',
            'meetup': 'User is discussing meetup logistics'
        }
        
    def detect_stage(self, conversation_history, item_context):
        """Detect the current stage of the conversation."""
        prompt = f"""Given this conversation about a marketplace item:
            Product Context: {item_context}

            Conversation:
            {conversation_history}

            Which stage is this conversation in?
            1. Questions about the product
            2. Price negotiation
            3. Scheduling meetup
            Respond with just the number (1, 2, or 3)."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=5,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        try: 
            response = message.content[0].text
            print(f"Extracted text: {response}")
            return int(response)
        
        except Exception as e:
            print(f"Error parsing stage: {e}")
            return 1  

    def generate_response(self, conversation_history, item_context, stage):
        stage_prompts = {
            1: f"""You are a helpful marketplace seller assistant. Given the following context about an item and conversation history, provide a friendly and informative response to questions about the product:
- make your response 1 to 2 sentences
- don't list any unnecessary details
- talk casually
Product Context: {item_context}
Conversation History: {conversation_history}
Focus on addressing specific product questions while being helpful and professional.""",
            
            2: f"""You are a marketplace seller assistant handling price negotiations. Given the following context and conversation, provide a response that:
- Is professional and courteous
- Considers the original price and any reasonable offers
- Maintains a firm but fair negotiating position
- make your response 1 to 2 sentences 
- don't list any unnecessary details
- talk casually
Product Context: {item_context}
Conversation History: {conversation_history}""",
            
            3: f"""You are a marketplace seller assistant coordinating a meetup. Given the following context and conversation, provide a response that:
- Be insistent that the meeting location must be at the seller's address if the item is not transportable. Otherwise, meet at UCSB Library
- Proposes clear meeting times
- make your response 1 to 2 sentences
- don't list any unnecessary details
- talk casually
Product Context: {item_context}
Conversation History: {conversation_history}"""
        }

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            temperature=0.7,
            messages=[{"role": "user", "content": stage_prompts[stage]}]
        )
        return message.content[0].text
    
    def get_status(self, conversation_history, response):
        prompt = f"""Given this marketplace conversation and the AI's response, determine the current status of the item. Choose from: unlisted, listed, negotiating, scheduled, sold.

Conversation History:
{conversation_history}

AI's Response:
{response}

Rules:
- If discussing price/offers -> "negotiating"
- If setting up meeting time/place -> "scheduled"
- If item is marked as sold -> "sold"
- If just answering questions -> "listed"
- If no listing found -> "unlisted"

Respond with just one word out of these: unlisted, listed, negotiating, scheduled, sold."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=20,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        response = message.content[0].text.lower()
        print("actual response: ", response)
        if response not in ["unlisted", "listed", "negotiating", "scheduled", "sold"]:
            return "listed"
        return response
