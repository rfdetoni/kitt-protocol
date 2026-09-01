# Manual do K.I.T.T. Protocol (`kitt-protocol`)

> Contratos de dados canônicos, esquemas de validação, Envelopes Protocol-V1 e SDKs multiplataforma para **Rust**, **Python** e **TypeScript**.

---

## 1. Visão Geral e Arquitetura

O **`kitt-protocol`** define a camada de comunicação padronizada de todo o ecossistema K.I.T.T.
Ele garante que eventos, mensagens de chat, streaming, contexto de execução, transcrição de áudio e comandos de memória possuam interoperabilidade de tipo estrita entre componentes compilados em Rust, Python e Node.js/TypeScript.

### Estrutura do Repositório:
- **`src/`**: Crate Rust canônica com estruturas `Envelope`, `Message`, `Event` e deserialização de alta performance.
- **`sdk/python/`**: SDK Python com dataclasses e validação de schema canônico.
- **`sdk/typescript/`**: Tipos TypeScript e parsers para browsers, Node.js e Tauri.
- **`fixtures/`**: Envelopes canônicos em JSON utilizados para teste de conformidade cruzada.

---

## 2. Requisitos de Sistema

- **Rust**: 1.80+ (com `cargo`)
- **Python**: 3.12+
- **Node.js**: 20+ e `npm`

---

## 3. Instalação e Compilação por Sistema Operacional

### 🐧 A. LINUX

```bash
# 1. Compilar crate Rust e rodar testes
cargo build --release
cargo test

# 2. Instalar SDK Python em modo desenvolvimento
pip install -e sdk/python

# 3. Instalar dependências e validar SDK TypeScript
npm ci
npm test
```

### 🍏 B. macOS

```bash
# 1. Compilação Rust
cargo build --release
cargo test

# 2. Instalação Python SDK
python3 -m pip install -e sdk/python

# 3. Validação TypeScript SDK
npm ci
npm test
```

### 🪟 C. WINDOWS (PowerShell)

```powershell
# 1. Compilação Rust
cargo build --release
cargo test

# 2. Instalação Python SDK
python -m pip install -e sdk/python

# 3. Validação TypeScript SDK
npm ci
npm test
```

---

## 4. Guia de Uso dos SDKs

### Exemplo em Rust:
```rust
use kitt_protocol::{Envelope, ProtocolVersion};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let raw_json = r#"{"version":"1.0","id":"req-001","type":"ping","payload":{}}"#;
    let envelope: Envelope = serde_json::from_str(raw_json)?;
    
    assert_eq!(envelope.version, ProtocolVersion::V1);
    println!("Envelope recebido: {} [{}]", envelope.id, envelope.message_type);
    Ok(())
}
```

### Exemplo em Python:
```python
from kitt_protocol import parse_envelope, Envelope

payload = '{"version": "1.0", "id": "msg-123", "type": "chat.request", "payload": {"content": "Olá"}}'
envelope = parse_envelope(payload)
print(f"ID: {envelope.id} | Tipo: {envelope.type}")
```

### Exemplo em TypeScript:
```typescript
import { parseEnvelope, Envelope } from '@kitt/protocol';

const raw = '{"version":"1.0","id":"evt-456","type":"agent.turn","payload":{"status":"ok"}}';
const envelope: Envelope = parseEnvelope(raw);
console.log(`Recebido evento: ${envelope.type}`);
```

---

## 5. Validação e Testes de Conformidade

Execute a suíte de testes cruzada em qualquer sistema operacional:

```bash
# Validação Rust
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test

# Validação Python
PYTHONPATH=sdk/python python3 -m unittest discover sdk/python/tests

# Validação TypeScript / Fixtures
npm test
```
