import sys
from pathlib import Path
import time
import threading
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_CALL_DELAY_SECONDS

T = TypeVar("T", bound=BaseModel)


class GeminiQueueService:
    """Manages Gemini API requests with sequential queuing, retries, and fallback."""

    def __init__(
        self,
        model_name: str = GEMINI_MODEL,
        delay_seconds: float = GEMINI_CALL_DELAY_SECONDS,
    ):
        self.model_name = model_name
        self.delay_seconds = delay_seconds
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self._lock = threading.Lock()
        self._last_call_time = 0.0

    def _wait_for_rate_limit(self):
        """Enforces a minimum cooldown period between consecutive API requests."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self.delay_seconds:
            sleep_needed = self.delay_seconds - elapsed
            print(f"[GeminiQueue] Rate limiting: cooling down for {sleep_needed:.2f}s...")
            time.sleep(sleep_needed)
        self._last_call_time = time.time()

    def _execute_with_retry(self, execute_fn):
        """Executes API call exclusively on the configured model with retries on server load."""
        last_error = None
        for attempt in range(1, 4):
            try:
                self._wait_for_rate_limit()
                return execute_fn(self.model_name)
            except ServerError as e:
                last_error = e
                wait_time = 10 * attempt
                print(f"[GeminiQueue] High server load on {self.model_name} (attempt {attempt}/3). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            except Exception as e:
                last_error = e
                print(f"[GeminiQueue] Request error: {e}")
                raise

        raise last_error or RuntimeError(f"Failed to execute call on {self.model_name} after retries.")

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Sends a request through the queue and parses the response into a Pydantic schema."""
        with self._lock:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=system_instruction,
                temperature=0.7,
            )

            def _call(model_id: str):
                response = self.client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=config,
                )
                return response.parsed

            return self._execute_with_retry(_call)

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Sends a request through the queue and returns raw generated text."""
        with self._lock:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )

            def _call(model_id: str):
                response = self.client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=config,
                )
                return response.text

            return self._execute_with_retry(_call)


# Global shared instance
llm_service = GeminiQueueService()


if __name__ == "__main__":
    print("--- Testing GeminiQueueService with 3s Rate Limiting ---")
    
    class PingTest(BaseModel):
        status: str
        message: str

    print("Sending Request 1...")
    start_t = time.time()
    res1 = llm_service.generate_structured(
        prompt="Respond with status 'active' and a short hello message.",
        response_schema=PingTest,
    )
    print(f"Result 1 in {time.time() - start_t:.2f}s: {res1}\n")

    print("Sending Request 2 (should trigger queue delay)...")
    start_t = time.time()
    res2 = llm_service.generate_structured(
        prompt="Respond with status 'completed' and a short farewell message.",
        response_schema=PingTest,
    )
    print(f"Result 2 in {time.time() - start_t:.2f}s: {res2}")
