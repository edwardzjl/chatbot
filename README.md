# Chatbot

**Chatbot** is a toy project that I built to ~~waste my time~~ escape the stress of work. It is a Single-page application (SPA) that lets you chat with an LLM agent named **Rei** (for now).

In this project, I'm trying to reproduce some key features of popular LLM-based chatbots like [ChatGPT](https://chatgpt.com/), [Gemini](https://gemini.google.com/) and [Le Chat](https://chat.mistral.ai/chat).

A demo is available at <https://chatbot.agi.zjuici.com/>, which connects to a self-hosted LLM service. However, please note that this is just for demonstration purposes — it’s not production-ready and may go down at any time for any reason.

Also, I’m still quite new to web development (HTML, CSS, JavaScript, React, etc.), so the code in the `web` directory (or even the entire project :worried:) might not be the most aesthetically pleasing. If that's the case, feel free to open an issue or submit a pull request to help me improve things. :wink:

## Key Features

I’ve already implemented some key features for the agent — although many (if not all) are still quite rough around the edges.

### Tool Usage

**Rei** can use external tools to be more helpful. Currently, two tools are available:

- Web Search: **Rei** can search the internet using a `web-search` tool powered by [SerpApi](https://serpapi.com/).
- Weather Forcast: **Rei** Rei can fetch weather information using a `weather-forecast` tool backed by [Open-meteo](https://open-meteo.com/)

More tools are planned, I want to make **Rei** a useful daily assistant! :smirk:

### Multi Modal Inputs

**Rei** supports text, image, and video input. However, I haven’t found any multi-modal model that performs well and supports tool usage effectively.

Given my personal priorities, I’ve chosen to prioritize tool usage and temporarily disabled the multi-modal input button. If you know of any good multi-modal models that work well with tool usage, please let me know!

### Reasoning

Chatbot supports reasoning models like [deepseek-ai/DeepSeek-R1-Distill-Qwen-32B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B) and [Qwen/QwQ-32B](https://huggingface.co/Qwen/QwQ-32B). Even if you're not using one of these models, the chatbot can still encourage reasoning behavior through prompt engineering.

However, as of this writing, most reasoning models either do not support tool usage or perform poorly when using tools. For that reason, it’s generally recommended to stick with a non-reasoning model if tool usage is important to you.

Also, when using reasoning models, their chat templates typically force them to "think" at the beginning of a response, following a "think-then-act" pattern. This isn't the case for non-reasoning models, which might "think" at the beginning, in the middle, or wherever it feels natural. I haven't forced them to start with a thinking step, because I feel the current behavior is more human-like -- as humans, we often pause mid-sentence to think, then continue.

That said, the current implementation of the chatbot always renders the "thinking" step at the beginning of the AI's response. So you might occasionally notice a bit of weirdness — like the response appears first, then jumps back to render the thought. This UX issue needs improvement, but I haven't yet decided how to best handle it.

### Working Memory

**Rei** has a short-term memory system, allowing her to remember recent conversations -- kind of like [working memory](https://en.wikipedia.org/wiki/Working_memory) in humans.

This is implemented by truncating the conversation history and passing the remaining messages to the LLM. The truncation strategy depends on the backend:

- If you are using [text-generation-inference](https://github.com/huggingface/text-generation-inference), [vLLM](https://github.com/vllm-project/vllm) or [llama.cpp](https://github.com/ggml-org/llama.cpp), **Rei** can count tokens in all messages (including the input), and drop the oldest ones until the total is under 90% of the model's context length.
- Otherwise, **Rei** falls back to keeping only the 20 most recent messages as working memory. (Note: In this case, you might encounter input-too-long issues.)

## Why chatbot

## Architecture

### Authentication

Chatbot incorporates OpenID Connect for user identification. It relies on an external OAuth Client [oidc-authservice](https://github.com/arrikto/oidc-authservice) to handle authentication and set a trusted `userid` Header to the downstream services. Alternatively, [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy), which is more actively maintained, can be used in place of `oidc-authservice`.

## Deployment

See [deployment instructions](./manifests/README.md)

## Configuration

Chatbot reads its configuration from environment variables. The following variables are currently supported:

#### LLM

A dictionary used to construct a [ChatOpenAI](https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html) instance, which serves as the core of the agent.

- type: `dict`
- default: `{"api_key": "NOT_SET"}`

#### SAFETY_LLM

A dictionary used to construct a [ChatOpenAI](https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html) instance that acts as a safety guard.

This is optional. Even if not set, the LLM you use may still have built-in safety mechanisms to reject harmful or toxic inputs. If you want to explicitly enable this feature, make sure you are using one of the Llama Guard 3 models.

- type: `dict | None`
- default: `None`

#### DB_PRIMARY_URL

The database url for reading and writing agent states and conversation metadata.

- type: `str`
- default: `sqlite+aiosqlite:///chatbot.sqlite`

#### DB_STANDBY_URL

An optional read-only database URL for agent states and conversation metadata. If not set, reads will fall back to `POSTGRES_PRIMARY_URL`.

- type: `str | None`
- default: `None`

#### SERP_API_KEY

The API key for [SearpApi](https://serpapi.com/), enabling **Rei** to use it as the `web-search` tool. You can get you key [here](https://serpapi.com/manage-api-key).

- type: `str | None`
- default: `None`

#### IPGEOLOCATION_API_KEY

The API key for [ipgeolocation](https://ipgeolocation.io/ip-location-api.html). Supplying this enables IP-to-location conversion, which can improve search relevance by passing the location as a parameter to the web-search tool.

- type: `str | None`
- default: `None`

#### OPENMETEO_API_KEY

The API key for [Open-meteo](https://open-meteo.com/).  Open-Meteo provides a free tier that doesn’t require an API key, so Rei can still use the `weather-forecast` tool without one. However, if you're using it in commercial projects, please consider subscribing to their API.

- type: `str | None`
- default: `None`

#### LOG_LEVEL

The logging level for the application.

- type: `str`
- default: `INFO`
