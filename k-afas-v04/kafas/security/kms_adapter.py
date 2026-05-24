"""
R28: KMS (Key Management System) 연동 모듈

목적: 암호화 키 관리를 외부 KMS에 위임하여 키 노출 방지.
     K-AFAS에서 직접 키를 저장하지 않고 KMS API를 통해서만 접근.

지원 KMS:
  - AWS KMS (기본)
  - Azure Key Vault
  - 국방 전용 KMS (인터페이스 동일)

용도:
  - 감사로그 서명 키
  - OAuth2 토큰 서명 키
  - 데이터 암호화 키 (DEK)
  - API 통신 TLS 인증서 관리

REJECT: 키를 코드/로그/응답에 평문 노출
"""
from __future__ import annotations
import time
import hashlib
import hmac
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class KeyPurpose(Enum):
    AUDIT_SIGNING = "audit_signing"          # 감사로그 SHA-256 서명
    TOKEN_SIGNING = "token_signing"          # OAuth2 토큰 서명
    DATA_ENCRYPTION = "data_encryption"      # DEK (Data Encryption Key)
    TLS_CERT = "tls_certificate"             # TLS 인증서
    HARNESS_SEAL = "harness_seal"            # 하네스 정책 봉인


class KeyStatus(Enum):
    ACTIVE = "active"
    ROTATING = "rotating"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class KeyMetadata:
    """키 메타데이터 (키 자체 아님, 참조 정보만)"""
    key_id: str
    purpose: KeyPurpose
    status: KeyStatus
    algorithm: str
    created_at: float
    expires_at: float
    rotation_days: int = 90
    last_rotated: float = 0.0

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def needs_rotation(self) -> bool:
        days_since = (time.time() - self.last_rotated) / 86400
        return days_since >= self.rotation_days


@dataclass
class KMSResponse:
    """KMS 작업 응답"""
    success: bool
    key_id: str = ""
    data: bytes = b""
    error: str = ""
    latency_ms: float = 0.0


# ── KMS 추상 인터페이스 ──────────────────────────────
class KMSProvider(ABC):
    """KMS 프로바이더 추상 클래스 — 교체 가능"""

    @abstractmethod
    def create_key(self, purpose: KeyPurpose, algorithm: str = "AES-256-GCM") -> KMSResponse:
        ...

    @abstractmethod
    def get_key_metadata(self, key_id: str) -> KeyMetadata | None:
        ...

    @abstractmethod
    def encrypt(self, key_id: str, plaintext: bytes) -> KMSResponse:
        ...

    @abstractmethod
    def decrypt(self, key_id: str, ciphertext: bytes) -> KMSResponse:
        ...

    @abstractmethod
    def sign(self, key_id: str, message: bytes) -> KMSResponse:
        ...

    @abstractmethod
    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        ...

    @abstractmethod
    def rotate_key(self, key_id: str) -> KMSResponse:
        ...

    @abstractmethod
    def revoke_key(self, key_id: str, reason: str) -> KMSResponse:
        ...


# ── 로컬 시뮬레이션 KMS (개발/테스트용) ──────────────
class LocalKMS(KMSProvider):
    """
    로컬 시뮬레이션 KMS — 실제 배포 시 AWS KMS 또는 국방 KMS로 교체.
    키는 메모리에만 존재, 프로세스 종료 시 소멸.
    """

    def __init__(self):
        self._keys: dict[str, bytes] = {}
        self._metadata: dict[str, KeyMetadata] = {}
        self._counter = 0

    def create_key(self, purpose: KeyPurpose, algorithm: str = "AES-256-GCM") -> KMSResponse:
        t0 = time.time()
        self._counter += 1
        key_id = f"kafas-key-{purpose.value}-{self._counter:04d}"

        # 256-bit 랜덤 키 생성
        key_material = os.urandom(32)
        self._keys[key_id] = key_material

        now = time.time()
        self._metadata[key_id] = KeyMetadata(
            key_id=key_id,
            purpose=purpose,
            status=KeyStatus.ACTIVE,
            algorithm=algorithm,
            created_at=now,
            expires_at=now + (365 * 86400),  # 1년
            last_rotated=now,
        )

        return KMSResponse(
            success=True,
            key_id=key_id,
            latency_ms=round((time.time() - t0) * 1000, 2),
        )

    def get_key_metadata(self, key_id: str) -> KeyMetadata | None:
        return self._metadata.get(key_id)

    def encrypt(self, key_id: str, plaintext: bytes) -> KMSResponse:
        t0 = time.time()
        key = self._keys.get(key_id)
        if not key:
            return KMSResponse(success=False, error="key_not_found")

        # 간이 XOR 암호화 (데모용 — 실제: AES-256-GCM)
        encrypted = bytes(a ^ b for a, b in zip(plaintext, (key * ((len(plaintext) // 32) + 1))[:len(plaintext)]))

        return KMSResponse(
            success=True,
            key_id=key_id,
            data=encrypted,
            latency_ms=round((time.time() - t0) * 1000, 2),
        )

    def decrypt(self, key_id: str, ciphertext: bytes) -> KMSResponse:
        # XOR은 대칭 — encrypt와 동일
        return self.encrypt(key_id, ciphertext)

    def sign(self, key_id: str, message: bytes) -> KMSResponse:
        t0 = time.time()
        key = self._keys.get(key_id)
        if not key:
            return KMSResponse(success=False, error="key_not_found")

        signature = hmac.new(key, message, hashlib.sha256).digest()
        return KMSResponse(
            success=True,
            key_id=key_id,
            data=signature,
            latency_ms=round((time.time() - t0) * 1000, 2),
        )

    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        key = self._keys.get(key_id)
        if not key:
            return False
        expected = hmac.new(key, message, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)

    def rotate_key(self, key_id: str) -> KMSResponse:
        t0 = time.time()
        meta = self._metadata.get(key_id)
        if not meta:
            return KMSResponse(success=False, error="key_not_found")

        # 새 키 생성 후 교체
        new_key = os.urandom(32)
        self._keys[key_id] = new_key
        meta.last_rotated = time.time()
        meta.status = KeyStatus.ACTIVE

        return KMSResponse(
            success=True,
            key_id=key_id,
            latency_ms=round((time.time() - t0) * 1000, 2),
        )

    def revoke_key(self, key_id: str, reason: str) -> KMSResponse:
        t0 = time.time()
        meta = self._metadata.get(key_id)
        if not meta:
            return KMSResponse(success=False, error="key_not_found")

        meta.status = KeyStatus.REVOKED
        del self._keys[key_id]

        return KMSResponse(
            success=True,
            key_id=key_id,
            latency_ms=round((time.time() - t0) * 1000, 2),
        )


# ── KMS 매니저 (통합 인터페이스) ──────────────────────
class KMSManager:
    """
    KMS 통합 관리자 — 키 생성/회전/폐기 + 자동 만료 점검

    사용법:
        mgr = KMSManager(provider=LocalKMS())
        audit_key = mgr.get_or_create(KeyPurpose.AUDIT_SIGNING)
        signed = mgr.sign(audit_key.key_id, b"audit_entry")
    """

    def __init__(self, provider: KMSProvider | None = None):
        self.provider = provider or LocalKMS()
        self._purpose_map: dict[KeyPurpose, str] = {}

    def get_or_create(self, purpose: KeyPurpose) -> KeyMetadata:
        """용도별 키 반환 (없으면 생성)"""
        key_id = self._purpose_map.get(purpose)
        if key_id:
            meta = self.provider.get_key_metadata(key_id)
            if meta and not meta.is_expired() and meta.status == KeyStatus.ACTIVE:
                return meta

        # 새 키 생성
        resp = self.provider.create_key(purpose)
        if resp.success:
            self._purpose_map[purpose] = resp.key_id
            return self.provider.get_key_metadata(resp.key_id)  # type: ignore
        raise RuntimeError(f"KMS key creation failed: {resp.error}")

    def sign(self, key_id: str, message: bytes) -> bytes:
        resp = self.provider.sign(key_id, message)
        if not resp.success:
            raise RuntimeError(f"KMS sign failed: {resp.error}")
        return resp.data

    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool:
        return self.provider.verify(key_id, message, signature)

    def check_rotations(self) -> list[str]:
        """회전 필요한 키 목록 반환"""
        needs_rotation = []
        for purpose, key_id in self._purpose_map.items():
            meta = self.provider.get_key_metadata(key_id)
            if meta and meta.needs_rotation():
                needs_rotation.append(key_id)
        return needs_rotation

    def rotate_all_due(self) -> int:
        """만료 임박 키 일괄 회전"""
        rotated = 0
        for key_id in self.check_rotations():
            resp = self.provider.rotate_key(key_id)
            if resp.success:
                rotated += 1
        return rotated
