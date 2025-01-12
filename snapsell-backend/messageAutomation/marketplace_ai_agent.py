from anthropic import Anthropic
from gcal import get_calendar_availability, create_calendar_event
import re
from datetime import datetime, timedelta

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
        availability = get_calendar_availability()
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
- If the buyer mentions a time to pick up their item, then check the availability to see if the seller is free
- If the buyer asks for your availability, choose a date from the following availability
Availability: {availability}
Product Context: {item_context}
Conversation History: {conversation_history}
"""
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
    
    def detect_meeting(self, conversation_history, response, item_title):
        current_date = datetime.now()
        prompt = f"""Given this conversation and response, determine if a specific meeting time has been agreed upon.
Conversation History:
{conversation_history}

AI's Response:
{response}

Rules:
- Look for specific times (e.g., "3:00 PM", "3PM", etc.)
- Look for specific dates (e.g., "tomorrow", "Monday", "January 15")
- Both time AND date must be present to consider it a confirmed meeting
- This is the current date {current_date}
- Make the scheduling in the year 2025

Return the response in this EXACT format:
date: YYYY-MM-DD
time: HH:MM AM/PM

If no meeting is confirmed, return exactly:
date: none
time: none"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=40,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text.strip()
        print("Claude response:", response_text)
        
        # Parse the response
        try:
            lines = response_text.split('\n')
            date = lines[0].split('date: ')[1].strip()
            time = lines[1].split('time: ')[1].strip()
            
            if date == 'none' or time == 'none':
                print("No confirmed meeting time found")
                return False
                
            # Combine date and time
            meeting_time = f"{date} {time}"
            print("Parsed meeting time:", meeting_time)
            
            # Parse the datetime
            start_time = datetime.strptime(meeting_time, "%Y-%m-%d %I:%M %p")
            print("Start time:", start_time)
            end_time = start_time + timedelta(minutes=30)
            
            event = create_calendar_event(
                summary=f"Meeting to Sell {item_title}",
                description=f"Meeting to discuss and complete {item_title} sale",
                start_time=start_time,
                end_time=end_time,
                attendees=None,
                location="UCSB Library"
            )
            
            if event:
                print(f"Meeting scheduled successfully for {meeting_time}")
                return True
                
        except Exception as e:
            print(f"Error processing meeting time: {e}")
            return False