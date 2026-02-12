import os
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from backend.ai.prompts import SYSTEM_PROMPT, DATA_CONTEXT, QUICK_QUERIES


class AirportChatbot:
    def __init__(self, reasoning_engine, config: Dict):
        self.reasoning_engine = reasoning_engine
        self.config = config
        self.client = None
        self.model = None

        provider = config["ai"].get("default_provider", "gemini")

        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and OPENAI_AVAILABLE:
                try:
                    self.client = OpenAI(
                        api_key=api_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                    )
                    self.model = config["ai"]["models"]["gemini"]
                    print(f"[+] Gemini client initialized (model: {self.model})")
                except Exception as e:
                    print(f"[!] Gemini init failed: {e}. Using fallback mode.")
                    self.client = None
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and OPENAI_AVAILABLE:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.model = config["ai"]["models"]["openai"]
                    print(f"[+] OpenAI client initialized (model: {self.model})")
                except Exception as e:
                    print(f"[!] OpenAI init failed: {e}. Using fallback mode.")
                    self.client = None

        self.conversation_history: List[Dict] = []

    def _build_data_context(self, query: str, date: datetime) -> str:
        context_parts = [DATA_CONTEXT, "", f"**Analyzing data for:** {date.strftime('%B %d, %Y')}", ""]
        query_lower = query.lower()

        if any(word in query_lower for word in ["queue", "wait", "compliance", "entry", "check-in", "security"]):
            queue_analysis = self.reasoning_engine.analyze_queue_compliance(date)
            context_parts.append("### Current Queue Compliance Status:")
            context_parts.append(f"- Overall Compliance: {queue_analysis['overall_compliance']:.1f}%")
            context_parts.append(f"- Zones Below Target: {queue_analysis['zones_below_target']}")
            context_parts.append(f"- Passengers Affected: {queue_analysis['total_pax_affected']:,}")
            if queue_analysis["worst_zones"]:
                context_parts.append("\nWorst Performing Zones:")
                for zone in queue_analysis["worst_zones"]:
                    context_parts.append(f"  - {zone['zone']}: {zone['actual_compliance_pct']:.1f}% (Target: 95%)")

        if any(word in query_lower for word in ["security", "lane", "reject", "screening"]):
            security_analysis = self.reasoning_engine.analyze_security_lanes(date)
            context_parts.append("\n### Security Lane Performance:")
            context_parts.append(f"- Total Cleared: {security_analysis['total_cleared']:,}")
            context_parts.append(f"- Average Reject Rate: {security_analysis['avg_reject_rate']}%")
            if security_analysis["high_reject_lanes"]:
                context_parts.append("\nHigh Reject Rate Lanes:")
                for lane in security_analysis["high_reject_lanes"][:3]:
                    context_parts.append(f"  - {lane['lane']}: {lane['reject_rate_pct']}% reject rate")

        if any(word in query_lower for word in ["passenger", "pax", "volume", "traffic", "peak"]):
            pax_analysis = self.reasoning_engine.analyze_passenger_volumes(date)
            context_parts.append("\n### Passenger Volumes:")
            context_parts.append(f"- Total: {pax_analysis['total_pax']:,}")
            context_parts.append(f"- Domestic: {pax_analysis['domestic_pax']:,}")
            context_parts.append(f"- International: {pax_analysis['international_pax']:,}")
            context_parts.append(f"- vs 7-day avg: {pax_analysis['vs_7day_pct']:+.1f}%")

        if any(word in query_lower for word in ["complaint", "feedback", "customer", "voc", "sentiment"]):
            voc_analysis = self.reasoning_engine.analyze_voc_sentiment(date)
            context_parts.append("\n### Voice of Customer:")
            context_parts.append(f"- Compliments: {voc_analysis['total_compliments']}")
            context_parts.append(f"- Complaints: {voc_analysis['total_complaints']}")
            context_parts.append(f"- Ratio: {voc_analysis['ratio']:.2f} (Sentiment: {voc_analysis['sentiment']})")

        # If no specific keywords matched, include everything for general queries
        if len(context_parts) <= 4:
            queue_analysis = self.reasoning_engine.analyze_queue_compliance(date)
            security_analysis = self.reasoning_engine.analyze_security_lanes(date)
            pax_analysis = self.reasoning_engine.analyze_passenger_volumes(date)
            voc_analysis = self.reasoning_engine.analyze_voc_sentiment(date)
            context_parts.append(f"\n### Overview:")
            context_parts.append(f"- Total PAX: {pax_analysis['total_pax']:,}")
            context_parts.append(f"- Queue Compliance: {queue_analysis['overall_compliance']:.1f}%")
            context_parts.append(f"- Avg Reject Rate: {security_analysis['avg_reject_rate']}%")
            context_parts.append(f"- VOC Ratio: {voc_analysis['ratio']:.2f}")

        return "\n".join(context_parts)

    def chat_stream(self, query: str, date: Optional[datetime] = None, history: Optional[List[Dict]] = None):
        """Streaming chat - yields chunks of text"""
        if date is None:
            date = datetime.strptime(self.config["data"]["report_date"], "%Y-%m-%d")

        data_context = self._build_data_context(query, date)

        if self.client is None:
            fallback = self._fallback_response(query, date)
            yield fallback
            return

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": data_context},
        ]

        if history:
            messages.extend(history[-10:])

        messages.append({"role": "user", "content": query})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config["ai"]["temperature"],
                max_tokens=self.config["ai"]["max_tokens"],
                stream=True,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"[!] OpenAI streaming error: {e}. Falling back to rule-based response.")
            yield self._fallback_response(query, date)

    def chat(self, query: str, date: Optional[datetime] = None, history: Optional[List[Dict]] = None) -> str:
        """Non-streaming chat - returns full response"""
        if date is None:
            date = datetime.strptime(self.config["data"]["report_date"], "%Y-%m-%d")

        data_context = self._build_data_context(query, date)

        if self.client is None:
            return self._fallback_response(query, date)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": data_context},
        ]

        if history:
            messages.extend(history[-10:])

        messages.append({"role": "user", "content": query})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config["ai"]["temperature"],
                max_tokens=self.config["ai"]["max_tokens"],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[!] OpenAI error: {e}. Falling back to rule-based response.")
            return self._fallback_response(query, date)

    def _fallback_response(self, query: str, date: datetime) -> str:
        query_lower = query.lower()

        if any(word in query_lower for word in ["queue", "compliance", "wait"]):
            queue_analysis = self.reasoning_engine.analyze_queue_compliance(date)
            response = f"## Queue Compliance Analysis - {date.strftime('%b %d, %Y')}\n\n"
            response += f"**Overall Compliance:** {queue_analysis['overall_compliance']:.1f}% (Target: 95%)\n\n"
            if queue_analysis["worst_zones"]:
                response += "### Worst Performing Zones:\n"
                for i, zone in enumerate(queue_analysis["worst_zones"][:3], 1):
                    response += f"{i}. **{zone['zone']}**: {zone['actual_compliance_pct']:.1f}% compliance\n"
                    response += f"   - Variance: {zone['variance_from_target']:.1f}%\n"
                    response += f"   - Passengers: {int(zone['pax_total']):,}\n\n"
            return response

        elif any(word in query_lower for word in ["security", "lane", "reject"]):
            security_analysis = self.reasoning_engine.analyze_security_lanes(date)
            response = f"## Security Lane Performance - {date.strftime('%b %d, %Y')}\n\n"
            response += f"**Total Cleared:** {security_analysis['total_cleared']:,}\n"
            response += f"**Average Reject Rate:** {security_analysis['avg_reject_rate']}%\n\n"
            if security_analysis["high_reject_lanes"]:
                response += "### High Reject Rate Lanes:\n"
                for lane in security_analysis["high_reject_lanes"]:
                    response += f"- **{lane['lane']}**: {lane['reject_rate_pct']}% ({lane['reject_count']} rejections)\n"
            return response

        else:
            return self.reasoning_engine.generate_executive_summary(date)
