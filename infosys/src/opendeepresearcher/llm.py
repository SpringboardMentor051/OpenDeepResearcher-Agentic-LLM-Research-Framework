from __future__ import annotations

from dataclasses import dataclass

import requests

from .config import Settings


class LLMError(RuntimeError):
	pass


@dataclass
class LLMClient:
	settings: Settings

	def generate(self, system_prompt: str, user_prompt: str) -> str:
		try:
			provider = self.settings.llm_provider
			if provider == "ollama":
				return self._generate_ollama(system_prompt, user_prompt)
			if provider in {"lmstudio", "openai_compatible"}:
				return self._generate_chat_completions(system_prompt, user_prompt)
			raise LLMError(f"Unsupported LLM provider: {provider}")
		except Exception as exc:
			if self.settings.llm_stub_on_error:
				return self._stub_response(system_prompt, user_prompt)
			if isinstance(exc, LLMError):
				raise
			raise LLMError(f"LLM request failed: {exc}") from exc

	def _generate_ollama(self, system_prompt: str, user_prompt: str) -> str:
		base_url = self.settings.llm_base_url.rstrip("/")
		payload = {
			"model": self.settings.llm_model,
			"system": system_prompt,
			"prompt": user_prompt,
			"stream": False,
			"num_predict": 500,
		}
		response = requests.post(
			f"{base_url}/api/generate",
			json=payload,
			timeout=self.settings.llm_timeout_seconds,
		)
		response.raise_for_status()
		body = response.json()
		text = str(body.get("response", "")).strip()
		if not text:
			raise LLMError("Empty response from Ollama")
		return text

	def _generate_chat_completions(self, system_prompt: str, user_prompt: str) -> str:
		base_url = self.settings.llm_base_url.rstrip("/")
		headers: dict[str, str] = {"Content-Type": "application/json"}
		if self.settings.llm_api_key:
			headers["Authorization"] = f"Bearer {self.settings.llm_api_key}"

		payload = {
			"model": self.settings.llm_model,
			"messages": [
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt},
			],
			"temperature": 0.2,
			"max_tokens": 500,
		}

		response = requests.post(
			f"{base_url}/v1/chat/completions",
			headers=headers,
			json=payload,
			timeout=self.settings.llm_timeout_seconds,
		)
		response.raise_for_status()
		body = response.json()
		choices = body.get("choices", [])
		if not choices:
			raise LLMError("No choices returned from chat completions API")
		message = choices[0].get("message", {})
		text = str(message.get("content", "")).strip()
		if not text:
			raise LLMError("Empty text returned from chat completions API")
		return text

	def _stub_response(self, system_prompt: str, user_prompt: str) -> str:
		planning_hints = ["planning assistant", "research plan", "concise research plan"]
		prompt_blob = f"{system_prompt}\n{user_prompt}".lower()
		if any(hint in prompt_blob for hint in planning_hints):
			return (
				"1) Clarify the scope and key questions.\n"
				"2) Collect 3 recent credible web sources.\n"
				"3) Compare findings and extract consensus.\n"
				"4) Summarize insights and propose next steps."
			)

		excerpt = user_prompt.strip().replace("\n", " ")[:180]
		return (
			"Stub draft (LLM unavailable).\n"
			"The orchestrator is connected: planning, retrieval, and writing steps executed successfully.\n"
			f"Prompt excerpt: {excerpt}"
		)
