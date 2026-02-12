"""
GenAI Chatbot for conversational operational insights
"""
import os
from typing import List, Dict, Optional
import json
from datetime import datetime


try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from src.ai.prompts import SYSTEM_PROMPT, DATA_CONTEXT, QUICK_QUERIES


class AirportChatbot:
    """
    Conversational AI chatbot for airport operations analysis
    """

    def __init__(self, reasoning_engine, config: Dict, provider: str = "openai"):
        """
        Initialize chatbot

        Args:
            reasoning_engine: OperationsReasoningEngine instance
            config: Configuration dictionary
            provider: AI provider ("openai", "anthropic", or "local")
        """
        self.reasoning_engine = reasoning_engine
        self.config = config
        self.provider = provider.lower()

        # Initialize AI client
        self.client = None
        self.model = None

        if self.provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.model = config['ai']['models']['openai']
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.model = config['ai']['models']['anthropic']

        # Conversation history
        self.conversation_history: List[Dict] = []

    def _build_data_context(self, query: str, date: datetime) -> str:
        """
        Build relevant data context based on the query

        Args:
            query: User query
            date: Date to analyze

        Returns:
            Formatted data context string
        """
        context_parts = [DATA_CONTEXT, ""]
        context_parts.append(f"**Analyzing data for:** {date.strftime('%B %d, %Y')}")
        context_parts.append("")

        # Determine what data to include based on query keywords
        query_lower = query.lower()

        if any(word in query_lower for word in ['queue', 'wait', 'compliance', 'entry', 'check-in', 'security']):
            # Add queue compliance data
            queue_analysis = self.reasoning_engine.analyze_queue_compliance(date)
            context_parts.append("### Current Queue Compliance Status:")
            context_parts.append(f"- Overall Compliance: {queue_analysis['overall_compliance']:.1f}%")
            context_parts.append(f"- Zones Below Target: {queue_analysis['zones_below_target']}")
            context_parts.append(f"- Passengers Affected: {queue_analysis['total_pax_affected']:,}")

            if queue_analysis['worst_zones']:
                context_parts.append("\nWorst Performing Zones:")
                for zone in queue_analysis['worst_zones']:
                    context_parts.append(f"  - {zone['zone']}: {zone['actual_compliance_pct']:.1f}% (Target: 95%)")

        if any(word in query_lower for word in ['security', 'lane', 'reject', 'screening']):
            # Add security lane data
            security_analysis = self.reasoning_engine.analyze_security_lanes(date)
            context_parts.append("\n### Security Lane Performance:")
            context_parts.append(f"- Total Cleared: {security_analysis['total_cleared']:,}")
            context_parts.append(f"- Average Reject Rate: {security_analysis['avg_reject_rate']}%")

            if security_analysis['high_reject_lanes']:
                context_parts.append("\nHigh Reject Rate Lanes:")
                for lane in security_analysis['high_reject_lanes'][:3]:
                    context_parts.append(f"  - {lane['lane']}: {lane['reject_rate_pct']}% reject rate")

        if any(word in query_lower for word in ['passenger', 'pax', 'volume', 'traffic', 'peak']):
            # Add passenger volume data
            pax_analysis = self.reasoning_engine.analyze_passenger_volumes(date)
            context_parts.append("\n### Passenger Volumes:")
            context_parts.append(f"- Total: {pax_analysis['total_pax']:,}")
            context_parts.append(f"- Domestic: {pax_analysis['domestic_pax']:,}")
            context_parts.append(f"- International: {pax_analysis['international_pax']:,}")
            context_parts.append(f"- vs 7-day avg: {pax_analysis['vs_7day_pct']:+.1f}%")

            if pax_analysis['peak_hours']:
                context_parts.append("\nPeak Hours:")
                for peak in pax_analysis['peak_hours']:
                    context_parts.append(f"  - {peak['hour']:02d}:00 - {peak['volume']:,} passengers")

        if any(word in query_lower for word in ['complaint', 'feedback', 'customer', 'voc', 'sentiment']):
            # Add VOC data
            voc_analysis = self.reasoning_engine.analyze_voc_sentiment(date)
            context_parts.append("\n### Voice of Customer:")
            context_parts.append(f"- Compliments: {voc_analysis['total_compliments']}")
            context_parts.append(f"- Complaints: {voc_analysis['total_complaints']}")
            context_parts.append(f"- Ratio: {voc_analysis['ratio']:.2f} (Sentiment: {voc_analysis['sentiment']})")

            if voc_analysis['negative_messages']:
                context_parts.append("\nRecent Negative Feedback:")
                for msg in voc_analysis['negative_messages'][:3]:
                    context_parts.append(f"  - \"{msg['message']}\" ({msg['terminal']}, {msg['department']})")

        return "\n".join(context_parts)

    def chat(self, query: str, date: Optional[datetime] = None) -> str:
        """
        Process a user query and return AI-generated response

        Args:
            query: User question/query
            date: Date to analyze (defaults to report date from config)

        Returns:
            AI-generated response
        """
        if date is None:
            date = datetime.strptime(self.config['data']['report_date'], '%Y-%m-%d')

        # Build context
        data_context = self._build_data_context(query, date)

        # If no AI client available, return rule-based response
        if self.client is None:
            return self._fallback_response(query, date)

        # Build messages for AI
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": data_context}
        ]

        # Add conversation history (last 5 exchanges)
        messages.extend(self.conversation_history[-10:])

        # Add current query
        messages.append({"role": "user", "content": query})

        try:
            # Call AI based on provider
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.config['ai']['temperature'],
                    max_tokens=self.config['ai']['max_tokens']
                )
                ai_response = response.choices[0].message.content

            elif self.provider == "anthropic":
                # Convert messages format for Anthropic
                system_msgs = [m['content'] for m in messages if m['role'] == 'system']
                user_msgs = [m for m in messages if m['role'] != 'system']

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.config['ai']['max_tokens'],
                    temperature=self.config['ai']['temperature'],
                    system="\n\n".join(system_msgs),
                    messages=user_msgs
                )
                ai_response = response.content[0].text

            else:
                ai_response = self._fallback_response(query, date)

            # Store in conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            return ai_response

        except Exception as e:
            return f"⚠️ Error generating AI response: {str(e)}\n\nPlease check your API key configuration or try the fallback analysis mode."

    def _fallback_response(self, query: str, date: datetime) -> str:
        """
        Generate rule-based response when AI is not available

        Args:
            query: User query
            date: Date to analyze

        Returns:
            Rule-based response
        """
        query_lower = query.lower()

        # Queue compliance query
        if any(word in query_lower for word in ['queue', 'compliance', 'wait']):
            queue_analysis = self.reasoning_engine.analyze_queue_compliance(date)
            response = f"## Queue Compliance Analysis - {date.strftime('%b %d, %Y')}\n\n"
            response += f"**Overall Compliance:** {queue_analysis['overall_compliance']:.1f}% (Target: 95%)\n\n"

            if queue_analysis['worst_zones']:
                response += "### Worst Performing Zones:\n"
                for i, zone in enumerate(queue_analysis['worst_zones'][:3], 1):
                    response += f"{i}. **{zone['zone']}**: {zone['actual_compliance_pct']:.1f}% compliance\n"
                    response += f"   - Variance: {zone['variance_from_target']:.1f}%\n"
                    response += f"   - Passengers: {int(zone['pax_total']):,}\n\n"

            return response

        # Security lanes query
        elif any(word in query_lower for word in ['security', 'lane', 'reject']):
            security_analysis = self.reasoning_engine.analyze_security_lanes(date)
            response = f"## Security Lane Performance - {date.strftime('%b %d, %Y')}\n\n"
            response += f"**Total Cleared:** {security_analysis['total_cleared']:,}\n"
            response += f"**Average Reject Rate:** {security_analysis['avg_reject_rate']}%\n\n"

            if security_analysis['high_reject_lanes']:
                response += "### High Reject Rate Lanes:\n"
                for lane in security_analysis['high_reject_lanes']:
                    response += f"- **{lane['lane']}**: {lane['reject_rate_pct']}% ({lane['reject_count']} rejections)\n"

            return response

        # General summary
        else:
            return self.reasoning_engine.generate_executive_summary(date)

    def get_quick_queries(self) -> List[str]:
        """Return list of suggested quick queries"""
        return QUICK_QUERIES

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
