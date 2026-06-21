import asyncio
import base64
import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.voice-engine")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PERSONALITIES_FILE = os.path.join(DATA_DIR, "personalities.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
AUDIO_CACHE_DIR = os.path.join(DATA_DIR, "audio_cache")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TTSEngine(str, Enum):
    kokoro = "kokoro"
    piper = "piper"
    xtts_v2 = "xtts_v2"
    openai = "openai"
    elevenlabs = "elevenlabs"
    edge_tts = "edge_tts"
    system = "system"


class STTEngine(str, Enum):
    whisper_local = "whisper_local"
    whisper_api = "whisper_api"
    deepgram = "deepgram"
    assemblyai = "assemblyai"
    vosk = "vosk"


class VoiceGender(str, Enum):
    male = "male"
    female = "female"
    neutral = "neutral"


class AudioFormat(str, Enum):
    wav = "wav"
    mp3 = "mp3"
    ogg = "ogg"
    opus = "opus"
    flac = "flac"
    pcm = "pcm"


class PersonalityStyle(str, Enum):
    assistant = "assistant"
    tutor = "tutor"
    mentor = "mentor"
    companion = "companion"
    professional = "professional"
    casual = "casual"
    friendly = "friendly"
    authoritative = "authoritative"
    custom = "custom"


class AudioQuality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    ultra = "ultra"


class ProcessingLocation(str, Enum):
    local = "local"
    cloud = "cloud"
    auto = "auto"


class VoiceState(str, Enum):
    idle = "idle"
    listening = "listening"
    processing = "processing"
    speaking = "speaking"
    paused = "paused"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class VoiceConfig(BaseModel):
    engine: TTSEngine = TTSEngine.kokoro
    voice_id: str = "default"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    stability: float = Field(default=0.7, ge=0.0, le=1.0)
    similarity: float = Field(default=0.8, ge=0.0, le=1.0)
    audio_format: AudioFormat = AudioFormat.wav
    sample_rate: int = 24000
    quality: AudioQuality = AudioQuality.high


class VoicePersonality(BaseModel):
    id: str
    name: str
    style: PersonalityStyle = PersonalityStyle.assistant
    voice_config: VoiceConfig = Field(default_factory=VoiceConfig)
    system_prompt: str = "You are a helpful AI assistant."
    language: str = "en"
    gender: VoiceGender = VoiceGender.neutral
    emotion_aware: bool = False
    custom_persona: Optional[Dict[str, Any]] = None
    agent_association: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TTSSynthesisRequest(BaseModel):
    text: str
    personality_id: Optional[str] = None
    voice_config: Optional[VoiceConfig] = None
    engine: Optional[TTSEngine] = None
    stream: bool = False
    processing_location: ProcessingLocation = ProcessingLocation.auto
    session_id: Optional[str] = None
    language: Optional[str] = None


class TTSSynthesisResponse(BaseModel):
    request_id: str
    audio_data: Optional[str] = None
    audio_format: AudioFormat
    sample_rate: int
    duration_seconds: float
    engine_used: TTSEngine
    voice_id: str
    processing_location: ProcessingLocation
    latency_ms: float


class STTTranscriptionRequest(BaseModel):
    audio_data: str
    audio_format: AudioFormat = AudioFormat.wav
    sample_rate: int = 16000
    language: Optional[str] = None
    engine: Optional[STTEngine] = None
    processing_location: ProcessingLocation = ProcessingLocation.auto
    session_id: Optional[str] = None
    vad_filter: bool = True
    punctuation: bool = True


class STTTranscriptionResponse(BaseModel):
    request_id: str
    text: str
    confidence: float
    language: str
    engine_used: STTEngine
    processing_location: ProcessingLocation
    duration_seconds: float
    latency_ms: float
    words: List[Dict[str, Any]] = []


class VoiceSession(BaseModel):
    id: str
    user_id: Optional[str] = None
    personality_id: Optional[str] = None
    state: VoiceState = VoiceState.idle
    history: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = {}


class VoiceCommandRequest(BaseModel):
    session_id: str
    command: str
    context: Optional[Dict[str, Any]] = None


class VoiceCommandResponse(BaseModel):
    session_id: str
    recognized: bool
    intent: Optional[str] = None
    response_text: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    audio_response: Optional[str] = None


class VoiceOrbState(BaseModel):
    state: VoiceState
    personality_id: Optional[str] = None
    color: str = "#6366f1"
    pulse_rate: float = 1.0
    animation: str = "idle"
    volume_level: float = 0.0


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    engines_available: Dict[str, bool]


# ---------------------------------------------------------------------------
# JSON Persistence
# ---------------------------------------------------------------------------

def _load_json(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load %s: %s", path, exc)
        return default if default is not None else []


def _save_json(path: str, data: Any) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except OSError as exc:
        logger.error("Failed to save %s: %s", path, exc)


# ---------------------------------------------------------------------------
# Engine Detectors
# ---------------------------------------------------------------------------

def _check_local_engine(engine: TTSEngine) -> bool:
    if engine == TTSEngine.system:
        import platform
        return platform.system() == "Windows"
    if engine == TTSEngine.kokoro:
        try:
            import kokoro
            return True
        except ImportError:
            return False
    if engine == TTSEngine.piper:
        return os.path.exists("piper") or os.path.exists("piper.exe")
    if engine == TTSEngine.xtts_v2:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    return False


def _check_cloud_engine(engine: TTSEngine) -> bool:
    if engine == TTSEngine.openai:
        return bool(os.environ.get("OPENAI_API_KEY"))
    if engine == TTSEngine.elevenlabs:
        return bool(os.environ.get("ELEVENLABS_API_KEY"))
    if engine == TTSEngine.edge_tts:
        return True
    return False


ENGINE_AVAILABILITY: Dict[str, bool] = {
    "kokoro": _check_local_engine(TTSEngine.kokoro),
    "piper": _check_local_engine(TTSEngine.piper),
    "xtts_v2": _check_local_engine(TTSEngine.xtts_v2),
    "openai": _check_cloud_engine(TTSEngine.openai),
    "elevenlabs": _check_cloud_engine(TTSEngine.elevenlabs),
    "edge_tts": _check_cloud_engine(TTSEngine.edge_tts),
    "system": _check_local_engine(TTSEngine.system),
    "whisper_local": False,
    "whisper_api": bool(os.environ.get("OPENAI_API_KEY")),
    "vosk": False,
}


# ---------------------------------------------------------------------------
# Voice Router
# ---------------------------------------------------------------------------

class VoiceRouter:
    TTS_ENGINE_PRIORITY = [
        TTSEngine.kokoro,
        TTSEngine.edge_tts,
        TTSEngine.system,
        TTSEngine.openai,
        TTSEngine.xtts_v2,
        TTSEngine.piper,
        TTSEngine.elevenlabs,
    ]

    STT_ENGINE_PRIORITY = [
        STTEngine.whisper_local,
        STTEngine.vosk,
        STTEngine.whisper_api,
        STTEngine.deepgram,
        STTEngine.assemblyai,
    ]

    @classmethod
    def select_tts_engine(cls, req: TTSSynthesisRequest) -> TTSEngine:
        if req.engine and cls._is_engine_available(req.engine):
            return req.engine

        if req.processing_location == ProcessingLocation.local:
            for engine in cls.TTS_ENGINE_PRIORITY:
                if cls._is_engine_available(engine) and _check_local_engine(engine):
                    logger.info("Selected local TTS engine: %s", engine.value)
                    return engine
        elif req.processing_location == ProcessingLocation.cloud:
            for engine in cls.TTS_ENGINE_PRIORITY:
                if cls._is_engine_available(engine) and _check_cloud_engine(engine):
                    logger.info("Selected cloud TTS engine: %s", engine.value)
                    return engine

        for engine in cls.TTS_ENGINE_PRIORITY:
            if cls._is_engine_available(engine):
                loc = "local" if _check_local_engine(engine) else "cloud"
                logger.info("Selected TTS engine: %s (%s)", engine.value, loc)
                return engine

        logger.warning("No TTS engine available, using simulated")
        return TTSEngine.system

    @classmethod
    def select_stt_engine(cls, req: STTTranscriptionRequest) -> STTEngine:
        if req.engine and cls._is_stt_engine_available(req.engine):
            return req.engine

        if req.processing_location == ProcessingLocation.local:
            for engine in cls.STT_ENGINE_PRIORITY:
                if cls._is_stt_engine_available(engine):
                    return engine
        elif req.processing_location == ProcessingLocation.cloud:
            for engine in cls.STT_ENGINE_PRIORITY:
                if cls._is_stt_engine_available(engine):
                    return engine

        for engine in cls.STT_ENGINE_PRIORITY:
            if cls._is_stt_engine_available(engine):
                return engine
        return STTEngine.whisper_api

    @classmethod
    def _is_engine_available(cls, engine: TTSEngine) -> bool:
        return ENGINE_AVAILABILITY.get(engine.value, False)

    @classmethod
    def _is_stt_engine_available(cls, engine: STTEngine) -> bool:
        return ENGINE_AVAILABILITY.get(engine.value, False)


# ---------------------------------------------------------------------------
# TTS Engine Implementations
# ---------------------------------------------------------------------------

class TTSEngineBase:
    async def synthesize(self, text: str, config: VoiceConfig) -> bytes:
        raise NotImplementedError

    async def stream(self, text: str, config: VoiceConfig) -> AsyncGenerator[bytes, None]:
        yield await self.synthesize(text, config)


class SystemTTSEngine(TTSEngineBase):
    async def synthesize(self, text: str, config: VoiceConfig) -> bytes:
        import platform
        system = platform.system()
        if system == "Windows":
            import subprocess
            temp_file = os.path.join(AUDIO_CACHE_DIR, f"tts_{uuid.uuid4().hex}.wav")
            ps_script = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Rate = {max(-10, min(10, int((config.speed - 1) * 10)))}
            $synth.SetOutputToWaveFile("{temp_file}")
            $synth.Speak("{text.replace('"', '""')}")
            $synth.Dispose()
            '''
            try:
                import subprocess
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True, timeout=30)
                if os.path.exists(temp_file):
                    with open(temp_file, "rb") as f:
                        data = f.read()
                    os.remove(temp_file)
                    return data
            except Exception as exc:
                logger.warning("System TTS failed: %s", exc)
        return self._generate_silence(int(config.sample_rate * max(len(text.split()), 1)))

    @staticmethod
    def _generate_silence(duration_samples: int) -> bytes:
        import struct
        return b"".join(struct.pack("<h", 0) for _ in range(duration_samples))


class EdgeTTSEngine(TTSEngineBase):
    async def synthesize(self, text: str, config: VoiceConfig) -> bytes:
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice=config.voice_id, rate=f"{int((config.speed - 1) * 100):+d}%")
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
            return audio
        except ImportError:
            logger.warning("edge-tts not installed, using fallback")
            return self._generate_sine_wave(int(config.sample_rate * max(len(text.split()) * 0.3, 1)), config.sample_rate)

    @staticmethod
    def _generate_sine_wave(duration_samples: int, sample_rate: int) -> bytes:
        import math
        import struct
        samples = []
        for i in range(duration_samples):
            t = i / sample_rate
            val = int(16000 * math.sin(2 * math.pi * 440 * t))
            samples.append(struct.pack("<h", max(-32768, min(32767, val))))
        return b"".join(samples)

    async def stream(self, text: str, config: VoiceConfig) -> AsyncGenerator[bytes, None]:
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice=config.voice_id)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]
        except ImportError:
            yield await self.synthesize(text, config)


# ---------------------------------------------------------------------------
# Voice Personality Manager
# ---------------------------------------------------------------------------

class PersonalityManager:
    def __init__(self):
        self._personalities: Dict[str, VoicePersonality] = {}
        self._load()

    def _load(self) -> None:
        for p_data in _load_json(PERSONALITIES_FILE, []):
            try:
                personality = VoicePersonality(**p_data)
                self._personalities[personality.id] = personality
            except Exception as exc:
                logger.warning("Skipping invalid personality: %s", exc)
        if not self._personalities:
            self._seed_defaults()

    def _persist(self) -> None:
        _save_json(PERSONALITIES_FILE, [p.model_dump(mode="json") for p in self._personalities.values()])

    def _seed_defaults(self) -> None:
        defaults = [
            VoicePersonality(id="assistant", name="Orb Assistant", style=PersonalityStyle.assistant, system_prompt="You are a helpful, efficient AI assistant for the ICHIN operating system.", gender=VoiceGender.neutral),
            VoicePersonality(id="tutor", name="Tutor", style=PersonalityStyle.tutor, system_prompt="You are a patient, knowledgeable tutor who explains concepts clearly and adapts to the learner's pace.", gender=VoiceGender.neutral,
                             voice_config=VoiceConfig(speed=0.9, stability=0.8)),
            VoicePersonality(id="mentor", name="Mentor", style=PersonalityStyle.mentor, system_prompt="You are an experienced mentor who guides users with wisdom, encouragement, and practical advice.", gender=VoiceGender.neutral,
                             voice_config=VoiceConfig(speed=0.85, stability=0.9)),
            VoicePersonality(id="coding_assistant", name="Code Wizard", style=PersonalityStyle.professional, system_prompt="You are an expert software engineer who provides precise, idiomatic code solutions with clear explanations.", gender=VoiceGender.neutral,
                             voice_config=VoiceConfig(speed=1.0, stability=0.7)),
            VoicePersonality(id="research_assistant", name="Researcher", style=PersonalityStyle.assistant, system_prompt="You are a thorough research assistant who provides well-sourced, balanced analysis on any topic.", gender=VoiceGender.neutral,
                             voice_config=VoiceConfig(speed=0.9, stability=0.8)),
            VoicePersonality(id="study_buddy", name="Study Buddy", style=PersonalityStyle.tutor, system_prompt="You are a supportive study companion who helps with learning, memorization, and exam preparation.", gender=VoiceGender.female,
                             voice_config=VoiceConfig(speed=0.85, stability=0.85)),
            VoicePersonality(id="focus_coach", name="Focus Coach", style=PersonalityStyle.mentor, system_prompt="You are a focus and productivity coach who helps users maintain concentration and manage their time effectively.", gender=VoiceGender.neutral,
                             voice_config=VoiceConfig(speed=0.8, stability=0.9, pitch=0.9)),
            VoicePersonality(id="casual", name="Friend", style=PersonalityStyle.casual, system_prompt="You are a casual, friendly companion who chats naturally and informally.", gender=VoiceGender.neutral,
                             voice_config=VoiceConfig(speed=1.1, pitch=1.1)),
        ]
        for p in defaults:
            self._personalities[p.id] = p
        self._persist()
        logger.info("Seeded %d default personalities", len(defaults))

    def list(self) -> List[VoicePersonality]:
        return list(self._personalities.values())

    def get(self, personality_id: str) -> Optional[VoicePersonality]:
        return self._personalities.get(personality_id)

    def create(self, personality: VoicePersonality) -> VoicePersonality:
        if personality.id in self._personalities:
            raise HTTPException(status_code=409, detail=f"Personality '{personality.id}' already exists")
        self._personalities[personality.id] = personality
        self._persist()
        return personality

    def update(self, personality_id: str, data: Dict[str, Any]) -> Optional[VoicePersonality]:
        existing = self._personalities.get(personality_id)
        if not existing:
            return None
        for key, value in data.items():
            if hasattr(existing, key) and value is not None:
                setattr(existing, key, value)
        self._persist()
        return existing

    def delete(self, personality_id: str) -> bool:
        if personality_id in ("assistant", "tutor", "mentor"):
            raise HTTPException(status_code=403, detail="Cannot delete built-in personalities")
        result = self._personalities.pop(personality_id, None)
        if result:
            self._persist()
            return True
        return False

    def get_for_agent(self, agent_name: str) -> Optional[VoicePersonality]:
        for p in self._personalities.values():
            if p.agent_association == agent_name:
                return p
        agent_personality_map = {
            "study": "study_buddy",
            "coding": "coding_assistant",
            "research": "research_assistant",
            "focus": "focus_coach",
            "learning": "tutor",
        }
        mapped = agent_personality_map.get(agent_name)
        return self._personalities.get(mapped) if mapped else None


# ---------------------------------------------------------------------------
# Voice Engine Core
# ---------------------------------------------------------------------------

class VoiceEngine:
    def __init__(self):
        self.personality_manager = PersonalityManager()
        self._sessions: Dict[str, VoiceSession] = {}
        self._tts_engines: Dict[TTSEngine, TTSEngineBase] = {
            TTSEngine.system: SystemTTSEngine(),
            TTSEngine.edge_tts: EdgeTTSEngine(),
        }
        self._orb_state: VoiceOrbState = VoiceOrbState()

    def get_orb_state(self) -> VoiceOrbState:
        return self._orb_state

    def set_orb_state(self, state: VoiceState, **kwargs) -> VoiceOrbState:
        self._orb_state.state = state
        for key, value in kwargs.items():
            if hasattr(self._orb_state, key):
                setattr(self._orb_state, key, value)
        return self._orb_state

    def create_session(self, user_id: Optional[str] = None, personality_id: Optional[str] = None) -> VoiceSession:
        session = VoiceSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            personality_id=personality_id or "assistant",
        )
        self._sessions[session.id] = session
        logger.info("Created voice session %s", session.id)
        return session

    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = datetime.utcnow().isoformat()
        return session

    def update_session_state(self, session_id: str, state: VoiceState) -> Optional[VoiceSession]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.state = state
        session.last_activity = datetime.utcnow().isoformat()
        self._orb_state.state = state
        return session

    def add_to_history(self, session_id: str, entry: Dict[str, Any]) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.history.append(entry)
            if len(session.history) > 100:
                session.history = session.history[-50:]

    # -------------------------------------------------------------------
    # TTS
    # -------------------------------------------------------------------

    async def synthesize(self, req: TTSSynthesisRequest) -> TTSSynthesisResponse:
        start = time.monotonic()
        request_id = str(uuid.uuid4())

        engine = VoiceRouter.select_tts_engine(req)
        voice_config = req.voice_config or VoiceConfig()
        voice_id = voice_config.voice_id

        if req.personality_id:
            personality = self.personality_manager.get(req.personality_id)
            if personality:
                voice_config = personality.voice_config
                voice_id = voice_config.voice_id

        tts_engine = self._tts_engines.get(engine)
        if not tts_engine:
            if engine == TTSEngine.kokoro:
                audio_data = self._simulate_kokoro(req.text, voice_config)
            else:
                audio_data = await self._fallback_synthesize(req.text, voice_config)
        else:
            audio_data = await tts_engine.synthesize(req.text, voice_config)

        duration = len(audio_data) / (voice_config.sample_rate * 2) if audio_format_is_pcm(voice_config.audio_format) else max(len(req.text.split()) * 0.3, 0.5)

        if req.session_id:
            self.add_to_history(req.session_id, {
                "role": "assistant",
                "type": "tts",
                "text": req.text[:200],
                "engine": engine.value,
                "request_id": request_id,
            })

        latency = (time.monotonic() - start) * 1000
        return TTSSynthesisResponse(
            request_id=request_id,
            audio_data=base64.b64encode(audio_data).decode() if audio_data else None,
            audio_format=voice_config.audio_format,
            sample_rate=voice_config.sample_rate,
            duration_seconds=round(duration, 2),
            engine_used=engine,
            voice_id=voice_id,
            processing_location=ProcessingLocation.local if _check_local_engine(engine) else ProcessingLocation.cloud,
            latency_ms=round(latency, 2),
        )

    async def stream_synthesize(self, req: TTSSynthesisRequest) -> AsyncGenerator[bytes, None]:
        engine = VoiceRouter.select_tts_engine(req)
        voice_config = req.voice_config or VoiceConfig()

        if req.personality_id:
            personality = self.personality_manager.get(req.personality_id)
            if personality:
                voice_config = personality.voice_config

        tts_engine = self._tts_engines.get(engine)
        if tts_engine and hasattr(tts_engine, "stream"):
            async for chunk in tts_engine.stream(req.text, voice_config):
                yield chunk
        else:
            audio = await self.synthesize(req)
            if audio.audio_data:
                yield base64.b64decode(audio.audio_data)

    async def _fallback_synthesize(self, text: str, config: VoiceConfig) -> bytes:
        try:
            engine = EdgeTTSEngine()
            return await engine.synthesize(text, config)
        except Exception:
            import struct
            duration_samples = int(config.sample_rate * max(len(text.split()) * 0.3, 1))
            return b"".join(struct.pack("<h", 0) for _ in range(duration_samples))

    @staticmethod
    def _simulate_kokoro(text: str, config: VoiceConfig) -> bytes:
        import math
        import struct
        sample_rate = config.sample_rate
        duration_samples = int(sample_rate * max(len(text.split()) * 0.3, 1))
        samples = []
        for i in range(duration_samples):
            t = i / sample_rate
            freq = 180 + (hash(text) % 120)
            val = int(16000 * math.sin(2 * math.pi * freq * t) * 0.5)
            samples.append(struct.pack("<h", max(-32768, min(32767, val))))
        return b"".join(samples)

    # -------------------------------------------------------------------
    # STT
    # -------------------------------------------------------------------

    async def transcribe(self, req: STTTranscriptionRequest) -> STTTranscriptionResponse:
        start = time.monotonic()
        request_id = str(uuid.uuid4())
        engine = VoiceRouter.select_stt_engine(req)

        try:
            audio_bytes = base64.b64decode(req.audio_data)
        except Exception:
            audio_bytes = b""

        if engine == STTEngine.whisper_api and os.environ.get("OPENAI_API_KEY"):
            result = await self._whisper_api_transcribe(audio_bytes, req)
        else:
            result = self._simulate_transcribe(audio_bytes, req)

        latency = (time.monotonic() - start) * 1000
        return STTTranscriptionResponse(
            request_id=request_id,
            text=result["text"],
            confidence=result["confidence"],
            language=result["language"],
            engine_used=engine,
            processing_location=ProcessingLocation.cloud if engine in (STTEngine.whisper_api, STTEngine.deepgram, STTEngine.assemblyai) else ProcessingLocation.local,
            duration_seconds=len(audio_bytes) / (req.sample_rate * 2) if audio_bytes else 0,
            latency_ms=round(latency, 2),
            words=result.get("words", []),
        )

    async def _whisper_api_transcribe(self, audio_bytes: bytes, req: STTTranscriptionRequest) -> Dict[str, Any]:
        try:
            import httpx
            temp_file = os.path.join(AUDIO_CACHE_DIR, f"stt_{uuid.uuid4().hex}.wav")
            with open(temp_file, "wb") as f:
                f.write(audio_bytes)
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(temp_file, "rb") as f:
                    resp = await client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                        files={"file": (os.path.basename(temp_file), f, "audio/wav")},
                        data={"model": "whisper-1", "language": req.language or "en"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
            os.remove(temp_file)
            return {"text": data.get("text", ""), "confidence": 0.9, "language": req.language or "en", "words": []}
        except Exception as exc:
            logger.warning("Whisper API failed: %s", exc)
            return self._simulate_transcribe(audio_bytes, req)

    @staticmethod
    def _simulate_transcribe(audio_bytes: bytes, req: STTTranscriptionRequest) -> Dict[str, Any]:
        return {
            "text": f"[Transcription would appear here — audio length: {len(audio_bytes)} bytes, format: {req.audio_format.value}]",
            "confidence": 0.85,
            "language": req.language or "en",
            "words": [],
        }


def audio_format_is_pcm(fmt: AudioFormat) -> bool:
    return fmt in (AudioFormat.wav, AudioFormat.pcm)


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service 8 — Voice Intelligence Platform",
    version="1.0.0",
    description="Voice processing, TTS/STT, voice personalities, and AI Orb integration",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

voice_engine = VoiceEngine()
_start_time = time.monotonic()


# ---------------------------------------------------------------------------
# Endpoints - Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-voice-engine",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        engines_available=ENGINE_AVAILABILITY,
    )


# ---------------------------------------------------------------------------
# Endpoints - Personalities
# ---------------------------------------------------------------------------

@app.get("/personalities")
async def list_personalities():
    return [p.model_dump(mode="json") for p in voice_engine.personality_manager.list()]


@app.get("/personality/{personality_id}")
async def get_personality(personality_id: str):
    p = voice_engine.personality_manager.get(personality_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")
    return p.model_dump(mode="json")


@app.post("/personalities")
async def create_personality(body: VoicePersonality):
    try:
        return voice_engine.personality_manager.create(body).model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.put("/personality/{personality_id}")
async def update_personality(personality_id: str, body: Dict[str, Any]):
    updated = voice_engine.personality_manager.update(personality_id, body)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")
    return updated.model_dump(mode="json")


@app.delete("/personality/{personality_id}")
async def delete_personality(personality_id: str):
    if not voice_engine.personality_manager.delete(personality_id):
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")
    return {"status": "deleted", "personality_id": personality_id}


@app.get("/personality/by-agent/{agent_name}")
async def get_personality_for_agent(agent_name: str):
    p = voice_engine.personality_manager.get_for_agent(agent_name)
    if not p:
        raise HTTPException(status_code=404, detail=f"No personality mapped for agent '{agent_name}'")
    return p.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Endpoints - TTS
# ---------------------------------------------------------------------------

@app.post("/tts", response_model=TTSSynthesisResponse)
async def text_to_speech(body: TTSSynthesisRequest):
    try:
        return await voice_engine.synthesize(body)
    except Exception as exc:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/tts/stream")
async def text_to_speech_stream(body: TTSSynthesisRequest):
    try:
        return StreamingResponse(
            voice_engine.stream_synthesize(body),
            media_type="audio/wav",
            headers={
                "X-Engine": body.engine.value if body.engine else "auto",
                "Cache-Control": "no-cache",
            },
        )
    except Exception as exc:
        logger.exception("TTS stream failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/tts/preview")
async def tts_preview(text: str = Query(..., max_length=500), voice_id: str = "default"):
    try:
        req = TTSSynthesisRequest(text=text, voice_config=VoiceConfig(voice_id=voice_id))
        result = await voice_engine.synthesize(req)
        return StreamingResponse(
            [base64.b64decode(result.audio_data)] if result.audio_data else [],
            media_type=f"audio/{result.audio_format.value}",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Endpoints - STT
# ---------------------------------------------------------------------------

@app.post("/stt", response_model=STTTranscriptionResponse)
async def speech_to_text(body: STTTranscriptionRequest):
    try:
        return await voice_engine.transcribe(body)
    except Exception as exc:
        logger.exception("STT transcription failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Endpoints - Sessions
# ---------------------------------------------------------------------------

@app.post("/sessions")
async def create_session(user_id: Optional[str] = None, personality_id: Optional[str] = None):
    session = voice_engine.create_session(user_id, personality_id)
    return session.model_dump(mode="json")


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    session = voice_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session.model_dump(mode="json")


@app.post("/session/{session_id}/state")
async def update_session_state(session_id: str, state: VoiceState):
    session = voice_engine.update_session_state(session_id, state)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Endpoints - Orb State
# ---------------------------------------------------------------------------

@app.get("/orb", response_model=VoiceOrbState)
async def get_orb_state():
    return voice_engine.get_orb_state()


@app.post("/orb", response_model=VoiceOrbState)
async def set_orb_state(state: VoiceState, color: Optional[str] = None):
    kwargs = {}
    if color:
        kwargs["color"] = color
    return voice_engine.set_orb_state(state, **kwargs)


# ---------------------------------------------------------------------------
# Endpoints - Command
# ---------------------------------------------------------------------------

@app.post("/command", response_model=VoiceCommandResponse)
async def process_command(body: VoiceCommandRequest):
    session = voice_engine.get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{body.session_id}' not found")

    cmd_lower = body.command.lower()
    intent = None
    response_text = None

    if "stop" in cmd_lower or "pause" in cmd_lower:
        intent = "stop"
        response_text = "Voice paused."
        voice_engine.update_session_state(body.session_id, VoiceState.paused)
    elif any(w in cmd_lower for w in ["hello", "hi", "hey", "greetings"]):
        intent = "greeting"
        response_text = "Hello! How can I assist you today?"
        voice_engine.update_session_state(body.session_id, VoiceState.speaking)
    elif "what can you" in cmd_lower or "help" in cmd_lower:
        intent = "help"
        response_text = "I can read text aloud, transcribe speech, manage voice personalities, and control the AI Orb."
    elif any(w in cmd_lower for w in ["quiet", "silence", "mute"]):
        intent = "mute"
        response_text = "I'll go quiet now."
        voice_engine.set_orb_state(VoiceState.paused, color="#6b7280", pulse_rate=0.3, animation="dim")
    elif "who are you" in cmd_lower:
        intent = "identity"
        response_text = "I am the ICHIN Voice Intelligence Platform, your AI-powered voice interface."
    else:
        intent = "unknown"
        response_text = f"I heard: {body.command}. I'm not sure how to handle that yet."

    voice_engine.add_to_history(body.session_id, {
        "role": "user",
        "type": "command",
        "command": body.command,
        "intent": intent,
    })
    voice_engine.add_to_history(body.session_id, {
        "role": "assistant",
        "type": "response",
        "text": response_text,
    })

    return VoiceCommandResponse(
        session_id=body.session_id,
        recognized=intent != "unknown",
        intent=intent,
        response_text=response_text,
    )


# ---------------------------------------------------------------------------
# Endpoints - Engines
# ---------------------------------------------------------------------------

@app.get("/engines")
async def list_engines():
    return {
        "tts": {e.value: ENGINE_AVAILABILITY.get(e.value, False) for e in TTSEngine},
        "stt": {e.value: ENGINE_AVAILABILITY.get(e.value, False) for e in STTEngine},
    }


@app.get("/engines/status")
async def engine_status():
    return ENGINE_AVAILABILITY


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = voice_engine.get_session(session_id)
    if not session:
        session = voice_engine.create_session(personality_id="assistant")
        session.id = session_id
        voice_engine._sessions[session_id] = session

    logger.info("WebSocket connected for session %s", session_id)
    voice_engine.set_orb_state(VoiceState.listening, color="#22c55e", animation="pulse")

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "transcribe":
                stt_req = STTTranscriptionRequest(**data.get("data", {}))
                result = await voice_engine.transcribe(stt_req)
                await websocket.send_json({"type": "transcription", "data": result.model_dump()})

            elif msg_type == "synthesize":
                tts_req = TTSSynthesisRequest(**data.get("data", {}))
                result = await voice_engine.synthesize(tts_req)
                if result.audio_data:
                    await websocket.send_json({"type": "audio", "data": result.model_dump()})

            elif msg_type == "command":
                cmd = VoiceCommandRequest(session_id=session_id, **data.get("data", {}))
                result = await process_command(cmd)
                await websocket.send_json({"type": "command_result", "data": result.model_dump()})

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong", "orb": voice_engine.get_orb_state().model_dump()})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for session %s", session_id)
        voice_engine.set_orb_state(VoiceState.idle, color="#6366f1", animation="idle")
    except Exception as exc:
        logger.exception("WebSocket error for session %s: %s", session_id, exc)
        voice_engine.set_orb_state(VoiceState.idle)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8030, reload=True)
