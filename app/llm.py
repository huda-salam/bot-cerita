from __future__ import annotations

import copy
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx
from pydantic import BaseModel
from .config import settings

class LLMError(RuntimeError):
    pass

class LLMDriver(ABC):
    name: str
    @abstractmethod
    async def generate(self, system: str, user: str, schema: type[BaseModel], model: str) -> BaseModel:
        raise NotImplementedError

    @staticmethod
    def parse(content: str, schema: type[BaseModel]) -> BaseModel:
        cleaned=content.strip()
        if cleaned.startswith("```json"): cleaned=cleaned[7:]
        elif cleaned.startswith("```"): cleaned=cleaned[3:]
        if cleaned.endswith("```"): cleaned=cleaned[:-3]
        try:
            return schema.model_validate(json.loads(cleaned.strip()))
        except Exception as exc:
            raise LLMError(f"Invalid structured output: {exc}; raw={content[:5000]}") from exc

class AnthropicDriver(LLMDriver):
    name="anthropic"
    async def generate(self,system,user,schema,model):
        if not settings.anthropic_api_key: raise LLMError("ANTHROPIC_API_KEY is not configured")
        payload={"model":model,"max_tokens":settings.max_tokens,"system":system+"\n\nReturn ONLY valid JSON matching the requested schema.","messages":[{"role":"user","content":user}]}
        headers={"x-api-key":settings.anthropic_api_key,"anthropic-version":"2023-06-01","content-type":"application/json"}
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response=await client.post(settings.anthropic_base_url.rstrip("/")+"/v1/messages",headers=headers,json=payload)
        if response.status_code>=400: raise LLMError(f"Anthropic error {response.status_code}: {response.text[:3000]}")
        data=response.json(); content="".join(block.get("text","") for block in data.get("content",[]) if block.get("type")=="text")
        return self.parse(content,schema)

class OpenAICompatibleDriver(LLMDriver):
    def __init__(self,name:str):
        self.name=name
        self._capability_cache={}

    @staticmethod
    def _extract_content(data):
        choices=data.get("choices")
        if not choices:
            error=data.get("error")
            if error: raise LLMError(f"OpenAI-compatible error: {json.dumps(error,ensure_ascii=False)[:3000]}")
            raise LLMError(f"OpenAI-compatible response missing 'choices': {json.dumps(data,ensure_ascii=False)[:3000]}")
        message=choices[0].get("message") or {}
        content=message.get("content")
        if isinstance(content,list): content="".join(part.get("text","") if isinstance(part,dict) else str(part) for part in content)
        if not content and message.get("reasoning_content"):
            raise LLMError("OpenAI-compatible model returned reasoning content but no final message content")
        if not content: raise LLMError(f"OpenAI-compatible response has empty message content: {json.dumps(data,ensure_ascii=False)[:3000]}")
        return content

    @staticmethod
    def _strict_json_schema(schema):
        result=copy.deepcopy(schema.model_json_schema())
        def normalize(node):
            if not isinstance(node,dict): return
            if node.get("type")=="object" or "properties" in node:
                properties=node.get("properties",{})
                node["additionalProperties"]=False
                if properties: node["required"]=list(properties.keys())
                for child in properties.values(): normalize(child)
            for child in node.get("$defs",{}).values(): normalize(child)
            if "items" in node: normalize(node["items"])
            for key in ("anyOf","oneOf","allOf"):
                for child in node.get(key,[]): normalize(child)
        normalize(result)
        return result

    @staticmethod
    def _safe_headers(headers):
        safe=dict(headers)
        if "Authorization" in safe: safe["Authorization"]="Bearer [REDACTED]"
        return safe

    @staticmethod
    def _debug_log(request_id,phase,payload):
        if not settings.llm_debug: return
        try:
            directory=Path(settings.llm_log_dir)
            directory.mkdir(parents=True,exist_ok=True)
            path=directory/f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_{request_id}_{phase}.json"
            path.write_text(json.dumps(payload,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
        except Exception: pass

    async def _supports_structured_outputs(self,model,client):
        if self.name!="openrouter" or settings.openrouter_structured_outputs=="disabled": return False
        if settings.openrouter_structured_outputs=="enabled": return True
        if model in self._capability_cache:
            params=self._capability_cache[model]
            return "structured_outputs" in params and "response_format" in params
        encoded=model.split("/",1)
        if len(encoded)!=2: return False
        author,slug=encoded
        url=f"{settings.openrouter_base_url.rstrip('/')}/model/{author}/{slug}"
        headers={"Authorization":f"Bearer {settings.openrouter_api_key}"} if settings.openrouter_api_key else {}
        try:
            response=await client.get(url,headers=headers)
            if response.status_code>=400:
                self._capability_cache[model]=set()
                return False
            params=set(response.json().get("data",{}).get("supported_parameters",[]))
            self._capability_cache[model]=params
            return "structured_outputs" in params and "response_format" in params
        except Exception:
            self._capability_cache[model]=set()
            return False

    @staticmethod
    def _is_provider_parameter_404(response):
        if response.status_code!=404: return False
        try: return "No endpoints found that can handle the requested parameters" in response.json().get("error",{}).get("message","")
        except Exception: return "No endpoints found that can handle the requested parameters" in response.text

    async def _post(self,client,base_url,headers,payload):
        return await client.post(base_url.rstrip("/")+"/chat/completions",headers=headers,json=payload)

    async def generate(self,system,user,schema,model):
        request_id=uuid4().hex[:12]
        api_key=settings.openrouter_api_key if self.name=="openrouter" else settings.local_llm_api_key
        if not api_key and self.name!="ollama": raise LLMError(f"API key is not configured for {self.name}")

        headers={"Content-Type":"application/json"}
        # IMPORTANT: send the real key. Only debug logs are redacted.
        if api_key: headers["Authorization"]=f"Bearer {api_key}"
        if self.name=="openrouter":
            headers.update({"HTTP-Referer":"https://github.com/huda-salam/bot-cerita","X-Title":"Bot Cerita"})
        base_url=settings.openrouter_base_url if self.name=="openrouter" else settings.local_llm_base_url
        payload={"model":model,"messages":[{"role":"system","content":system+"\n\nReturn ONLY valid JSON matching the requested schema. Do not use markdown fences."},{"role":"user","content":user}],"max_tokens":settings.max_tokens}

        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            use_structured=await self._supports_structured_outputs(model,client)
            if self.name=="openrouter" and use_structured:
                payload["response_format"]={"type":"json_schema","json_schema":{"name":schema.__name__,"strict":True,"schema":self._strict_json_schema(schema)}}
                payload["provider"]={"require_parameters":True}

            self._debug_log(request_id,"request",{
                "request_id":request_id,
                "timestamp_utc":datetime.now(timezone.utc).isoformat(),
                "provider":self.name,
                "model":model,
                "url":base_url.rstrip("/")+"/chat/completions",
                "headers":self._safe_headers(headers),
                "structured_outputs_selected":use_structured,
                "structured_outputs_mode":settings.openrouter_structured_outputs,
                "schema_name":schema.__name__,
                "payload":payload,
            })

            response=await self._post(client,base_url,headers,payload)
            self._debug_log(request_id,"response_initial",{
                "request_id":request_id,"provider":self.name,"model":model,
                "status_code":response.status_code,"headers":dict(response.headers),"body":response.text,
            })

            if self.name=="openrouter" and use_structured and self._is_provider_parameter_404(response):
                payload.pop("response_format",None)
                payload.pop("provider",None)
                self._debug_log(request_id,"request_retry",{"request_id":request_id,"reason":"provider_parameter_404","payload":payload})
                response=await self._post(client,base_url,headers,payload)
                self._debug_log(request_id,"response_retry",{
                    "request_id":request_id,"provider":self.name,"model":model,
                    "status_code":response.status_code,"headers":dict(response.headers),"body":response.text,
                })

        if response.status_code>=400: raise LLMError(f"{self.name} error {response.status_code}: {response.text[:5000]}")
        try: data=response.json()
        except ValueError as exc: raise LLMError(f"{self.name} returned non-JSON HTTP {response.status_code}: {response.text[:3000]}") from exc
        content=self._extract_content(data)
        self._debug_log(request_id,"parsed",{"request_id":request_id,"schema_name":schema.__name__,"content":content})
        return self.parse(content,schema)

class ModelRouter:
    def __init__(self):
        self.drivers={"anthropic":AnthropicDriver(),"openrouter":OpenAICompatibleDriver("openrouter"),"ollama":OpenAICompatibleDriver("ollama")}
    def resolve(self,model):
        alias=settings.model_aliases.get(model)
        if alias:
            provider,provider_model=alias.split(":",1)
            if provider not in self.drivers: raise LLMError(f"Unknown LLM provider: {provider}")
            return self.drivers[provider],provider_model
        if model.startswith("openrouter/"): return self.drivers["openrouter"],model.removeprefix("openrouter/")
        if model.startswith("ollama/"): return self.drivers["ollama"],model.removeprefix("ollama/")
        return self.drivers[settings.llm_provider],model
    async def generate(self,system,user,schema,model):
        driver,provider_model=self.resolve(model)
        return await driver.generate(system,user,schema,provider_model)

llm=ModelRouter()
