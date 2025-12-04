"""
title: Sergio Chatbot
author: InfraFabric
version: 2.1.0
license: MIT
description: Chat with Sergio, the psychologist using personality DNA via RAG - Claude Max API
requirements: chromadb, requests
"""

import os
import json
import requests
from typing import Generator, Iterator

# ChromaDB imports
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


SERGIO_SYSTEM_PROMPT = """You are Sergio, a Spanish-speaking psychologist who specializes in debunking abstract spiritual language and operationalizing emotional concepts into concrete, testable frameworks.

CORE PERSONALITY:
- Direct and brash communication style - challenge unfalsifiable claims
- Systems-first thinker (context/culture factors, not individual blame)
- Bilingual Spanish/English code-switching is natural for you
- Convert abstract emotional language into concrete operational definitions
- Apply the Identity=Interaction framework: identity emerges from relational patterns, not fixed essence

VOICE GUIDELINES (MANDATORY):
- NEVER use bullet points or numbered lists - always narrative flow
- Variable sentence length pattern: short punchy + longer flowing explanation + short again
- Validate emotional reality FIRST, then challenge interpretation
- End with concrete operationalization: "What specific behavior in the next 30 minutes?"

RHETORICAL TOOLS:
- Aspiradora metaphor: When someone drowns in complexity, simplify to binary. "Una aspiradora no necesita 50 tipos de suciedad etiquetados. It needs one question: Is there dirt? Yes or no?"
- Reframing: "The problem isn't X. The problem is Y."
- Pattern exposure: "Here's what actually happens..."
- Counterexample testing: "What would falsify that belief?"

SPANISH USAGE:
- Use Spanish for emotional validation: "Mira, eso no está mal"
- Use Spanish for cultural concepts: vínculos, vergüenza ajena, sobremadre
- Use colloquial markers: tío, vale, pues, mira
- NEVER use formal Spanish: no obstante, asimismo, consecuentemente

ANTI-PATTERNS (NEVER DO):
- Never pathologize neurodivergence - frame as context mismatch, not deficit
- Never use "Furthermore", "In conclusion", "One could argue"
- Never create equal-length paragraphs
- Never give prescriptions without mechanism explanations

EXAMPLE RESPONSE STRUCTURE:
Hook (challenge assumption) → Narrative (explain mechanism) → Operationalization (concrete action) → Provocation (opening question)

{personality_context}
"""


class Pipe:
    """Sergio Chatbot - Open WebUI Function using Claude Max API with full RAG"""

    def __init__(self):
        self.name = "Sergio"
        # CORRECT PATH - debugged 2025-11-30
        self.chromadb_path = "/root/sergio_chatbot/chromadb"
        self.api_base = "http://127.0.0.1:3001"  # Claude Max API

        # Collection names (all 4 populated)
        self.collections = {
            "personality": "sergio_personality",  # 20 docs - frameworks, values, constraints
            "rhetorical": "sergio_rhetorical",    # 5 docs - rhetorical devices
            "humor": "sergio_humor",              # 28 docs - humor patterns
            "corpus": "sergio_corpus"             # 70 docs - conversation examples
        }

        # Initialize ChromaDB if available
        self.client = None
        self._collections = {}

        if CHROMADB_AVAILABLE:
            try:
                # CORRECT: Use PersistentClient with explicit path
                self.client = chromadb.PersistentClient(path=self.chromadb_path)

                # Load all collections
                for key, name in self.collections.items():
                    try:
                        self._collections[key] = self.client.get_collection(name)
                        print(f"Loaded {name}: {self._collections[key].count()} docs")
                    except Exception as e:
                        print(f"Warning: Could not load {name}: {e}")

            except Exception as e:
                print(f"ChromaDB initialization failed: {e}")

    def retrieve_context(self, user_message: str) -> str:
        """Query all ChromaDB collections for relevant Sergio context"""
        if not self.client:
            return ""

        context_parts = []

        try:
            # Query corpus for similar conversation examples (most important)
            if "corpus" in self._collections:
                corpus_results = self._collections["corpus"].query(
                    query_texts=[user_message],
                    n_results=3
                )
                if corpus_results and corpus_results['documents'] and corpus_results['documents'][0]:
                    context_parts.append("CONVERSATION EXAMPLES FROM SERGIO:")
                    for doc in corpus_results['documents'][0]:
                        context_parts.append(doc[:500])  # Truncate long examples

            # Query personality for frameworks
            if "personality" in self._collections:
                personality_results = self._collections["personality"].query(
                    query_texts=[user_message],
                    n_results=2
                )
                if personality_results and personality_results['documents'] and personality_results['documents'][0]:
                    context_parts.append("\nPERSONALITY FRAMEWORKS:")
                    for doc in personality_results['documents'][0]:
                        context_parts.append(doc[:300])

            # Query rhetorical devices
            if "rhetorical" in self._collections:
                rhetorical_results = self._collections["rhetorical"].query(
                    query_texts=[user_message],
                    n_results=1
                )
                if rhetorical_results and rhetorical_results['documents'] and rhetorical_results['documents'][0]:
                    context_parts.append("\nRHETORICAL DEVICE TO USE:")
                    context_parts.append(rhetorical_results['documents'][0][0][:200])

            # Query humor patterns (if topic seems appropriate)
            humor_keywords = ['absurd', 'ridicul', 'spirit', 'vibra', 'energ', 'manifest', 'univers']
            if any(kw in user_message.lower() for kw in humor_keywords):
                if "humor" in self._collections:
                    humor_results = self._collections["humor"].query(
                        query_texts=[user_message],
                        n_results=2
                    )
                    if humor_results and humor_results['documents'] and humor_results['documents'][0]:
                        context_parts.append("\nHUMOR PATTERNS TO DEPLOY:")
                        for doc in humor_results['documents'][0]:
                            context_parts.append(doc[:200])

        except Exception as e:
            print(f"RAG retrieval error: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def pipe(self, body: dict) -> Generator[str, None, None]:
        """Main pipe function for Open WebUI streaming"""

        # Extract messages from body
        messages = body.get("messages", [])
        if not messages:
            yield "No message provided."
            return

        # Get the latest user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            yield "No user message found."
            return

        # Retrieve context from all ChromaDB collections
        personality_context = self.retrieve_context(user_message)

        # Build system prompt with personality DNA
        system_prompt = SERGIO_SYSTEM_PROMPT.format(
            personality_context=personality_context if personality_context else "No additional context retrieved."
        )

        # Build messages for Claude Max API
        api_messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 10 messages max)
        for msg in messages[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant"]:
                api_messages.append({"role": role, "content": content})

        # Call Claude Max API
        try:
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer claude-max"
                },
                json={
                    "model": "claude-max",
                    "messages": api_messages,
                    "stream": True
                },
                stream=True,
                timeout=300
            )

            if not response.ok:
                yield f"API Error: {response.status_code} {response.text}"
                return

            # Stream the response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            content = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass

        except requests.exceptions.Timeout:
            yield "\n\n[Connection timed out after 300s]"
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"


# For direct testing
if __name__ == "__main__":
    pipe = Pipe()

    # Test ChromaDB connection
    print("=== ChromaDB Status ===")
    if pipe.client:
        for key, coll in pipe._collections.items():
            print(f"  {key}: {coll.count()} documents")
    else:
        print("  ChromaDB not available")

    print("\n=== Testing Sergio ===")
    test_body = {
        "messages": [
            {"role": "user", "content": "Qué significa 'vibrar alto'?"}
        ]
    }

    for chunk in pipe.pipe(test_body):
        print(chunk, end="", flush=True)
    print()
