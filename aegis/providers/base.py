import abc
from aegis.core.models import ChatCompletionRequest, ChatCompletionResponse

class BaseLLMProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'gemini', 'openai', 'mock')."""
        pass

    @abc.abstractmethod
    async def generate(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute chat completion request and return unified ChatCompletionResponse."""
        pass
