from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WordCounterInput(BaseModel):
    """Input schema for WordCounterTool."""

    text: str = Field(..., description="The text to count words in.")


class WordCounterTool(BaseTool):
    name: str = "Word Counter Tool"
    description: str = "Counts the number of words in a given text. Pass the raw text directly, not as JSON."
    args_schema: type[BaseModel] = WordCounterInput

    def _run(self, text: str) -> int:
        # Handle case where LLM passes escaped JSON instead of raw text
        if text.strip().startswith('{"text": "') and text.strip().endswith('"}'):
            try:
                import json

                # Parse the JSON string properly
                parsed = json.loads(text.strip())
                text = parsed["text"]
            except (json.JSONDecodeError, KeyError):
                # If JSON parsing fails, fall back to raw text
                pass

        # Count the number of words in the text
        word_count = len(text.split())
        return word_count


if __name__ == "__main__":
    # Test the WordCounterTool
    tool = WordCounterTool()

    # Test with escaped JSON (what LLM currently sends) - matching the 361-word text
    test_text_escaped = """
    {\"text\": \"Empowering Autonomous AI Agents with Secure, Transparent Transactions\\n\\nIn our rapidly advancing digital landscape, AI agents are on the verge of revolutionizing how transactions are conducted. However, a critical barrier remains: the absence of a secure, autonomous financial transaction system allowing these agents to operate independently within digital ecosystems. This lack of infrastructure inhibits AI agents from reaching their full potential in automating processes and enabling seamless digital interactions.\\n\\nA Cutting-Edge Solution: AI-Powered Wallets\\n\\nOur solution is an AI-powered wallet system integrating advanced blockchain technology. This groundbreaking platform empowers AI agents to execute transactions securely, transparently, and at scale. By facilitating autonomous transactions across a myriad of applications\\u2014from supply chains to AI-driven marketplaces\\u2014we are not merely keeping pace with innovation; we are defining the future of digital interactions. Our technology aims to revolutionize the operations of AI agents online, ushering in an era where intelligent agents are primary drivers of economic activity.\\n\\nWhy Enrique Is the Ideal Co-Founder\\n\\nFacing such a formidable challenge requires the deep expertise of Enrique in AI systems engineering and infrastructure. His experience at Graphite highlights his capability in scaling Natural Language Processing (NLP) systems, expertise crucial for developing robust AI transaction architectures. Enrique's focus on agentic systems aligns seamlessly with our vision of enabling AI agents to autonomously navigate and transact within emerging digital ecosystems. His technical acumen and strategic insight fortify our confidence in overcoming the current limitations of AI transaction systems.\\n\\nA Market Ripe with Opportunity\\n\\nThe rising market demand for AI autonomy and blockchain integration offers a multi-billion-dollar frontier for innovation. Our target market spans businesses keen to leverage autonomous AI agents in areas like automated supply chain management, financial services, and decentralized applications. By tackling today's critical need for secure and scalable AI transactions, our platform not only addresses immediate industry challenges but also positions us as leaders at the forefront of the digital economy revolution.\\n\\nThrough our shared vision and complementary expertise, we are poised to solve existing challenges and set the standards for future digital economies driven by AI agents. Enrique, your collaboration is crucial to bringing this transformative vision to fruition, guiding us toward a successful, AI-empowered economic future.\"}"""

    # Test with the actual 361-word text you provided
    test_text_raw = """
Empowering Autonomous AI Agents with Secure, Transparent Transactions

In our rapidly advancing digital landscape, AI agents are on the verge of revolutionizing how transactions are conducted. However, a critical barrier remains: the absence of a secure, autonomous financial transaction system allowing these agents to operate independently within digital ecosystems. This lack of infrastructure inhibits AI agents from reaching their full potential in automating processes and enabling seamless digital interactions.

A Cutting-Edge Solution: AI-Powered Wallets

Our solution is an AI-powered wallet system integrating advanced blockchain technology. This groundbreaking platform empowers AI agents to execute transactions securely, transparently, and at scale. By facilitating autonomous transactions across a myriad of applications—from supply chains to AI-driven marketplaces—we are not merely keeping pace with innovation; we are defining the future of digital interactions. Our technology aims to revolutionize the operations of AI agents online, ushering in an era where intelligent agents are primary drivers of economic activity.

Why Enrique Is the Ideal Co-Founder

Facing such a formidable challenge requires the deep expertise of Enrique in AI systems engineering and infrastructure. His experience at Graphite highlights his capability in scaling Natural Language Processing (NLP) systems, expertise crucial for developing robust AI transaction architectures. Enrique’s focus on agentic systems aligns seamlessly with our vision of enabling AI agents to autonomously navigate and transact within emerging digital ecosystems. His technical acumen and strategic insight fortify our confidence in overcoming the current limitations of AI transaction systems.

A Market Ripe with Opportunity

The rising market demand for AI autonomy and blockchain integration offers a multi-billion-dollar frontier for innovation. Our target market spans businesses keen to leverage autonomous AI agents in areas like automated supply chain management, financial services, and decentralized applications. By tackling today’s critical need for secure and scalable AI transactions, our platform not only addresses immediate industry challenges but also positions us as leaders at the forefront of the digital economy revolution.

Through our shared vision and complementary expertise, we are poised to solve existing challenges and set the standards for future digital economies driven by AI agents. Enrique, your collaboration is crucial to bringing this transformative vision to fruition, guiding us toward a successful, AI-empowered economic future."""

    # Test both cases
    print("Testing escaped JSON (what LLM currently sends):")
    result_escaped = tool._run(text=test_text_escaped)
    print("Word Count:", result_escaped)

    print("\nTesting raw text (what it should be):")
    result_raw = tool._run(text=test_text_raw)
    print("Word Count:", result_raw)

    print(f"\nBoth should show the same count: {result_escaped == result_raw}")
