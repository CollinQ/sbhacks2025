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
            model="claude-3-sonnet-20240229",
            max_tokens=1,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        return int(message.content)

    def generate_response(self, conversation_history, item_context, stage):
        """Generate appropriate response based on conversation stage."""
        stage_prompts = {
            1: f"""You are a helpful marketplace seller assistant. Given the following context about an item and conversation history, provide a friendly and informative response to questions about the product:
Product Context: {item_context}
Conversation History: {conversation_history}
Focus on addressing specific product questions while being helpful and professional.""",
            
            2: f"""You are a marketplace seller assistant handling price negotiations. Given the following context and conversation, provide a response that:
- Is professional and courteous
- Considers the original price and any reasonable offers
- Maintains a firm but fair negotiating position
Product Context: {item_context}
Conversation History: {conversation_history}""",
            
            3: f"""You are a marketplace seller assistant coordinating a meetup. Given the following context and conversation, provide a response that:
- Suggests safe, public meeting locations
- Proposes clear meeting times
- Maintains professional communication
Product Context: {item_context}
Conversation History: {conversation_history}"""
        }

        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=150,
            temperature=0.7,
            messages=[{"role": "user", "content": stage_prompts[stage]}]
        )
        return message.content
