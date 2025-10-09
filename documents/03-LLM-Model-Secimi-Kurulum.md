# NETZ Informatique - LLM Model Seçimi ve Kurulum Rehberi

## 🤖 Model Seçim Kriterleri

### Gereksinimler
1. **Fransızca Dil Desteği** - Mükemmel seviyede
2. **Offline Çalışma** - İnternet bağlantısı gerektirmemeli
3. **Ticari Kullanım** - Lisans uygun olmalı
4. **Fine-tuning** - Şirket verilerine özel eğitim imkanı
5. **Performans** - Hızlı yanıt süresi (< 2 saniye)

## 📊 Önerilen Model Hiyerarşisi

### 1. Ana Model: **Mistral 7B Instruct v0.2**
```yaml
Model: mistralai/Mistral-7B-Instruct-v0.2
Parametre: 7 milyar
VRAM: ~14GB (FP16)
Lisans: Apache 2.0 (Ticari kullanıma uygun)
Dil: Mükemmel Fransızca desteği
```

**Avantajları:**
- Fransız yapımı, Fransızca optimize
- Düşük kaynak tüketimi
- Yüksek performans/maliyet oranı
- Fine-tuning friendly

### 2. Alternatif: **Llama 2 13B Chat**
```yaml
Model: meta-llama/Llama-2-13b-chat-hf
Parametre: 13 milyar  
VRAM: ~26GB (FP16)
Lisans: Custom (Ticari kullanım OK)
Dil: İyi Fransızca desteği
```

### 3. Premium Seçenek: **Mixtral 8x7B**
```yaml
Model: mistralai/Mixtral-8x7B-Instruct-v0.1
Parametre: 46.7 milyar (MoE)
VRAM: ~90GB (FP16) / ~25GB (4-bit)
Lisans: Apache 2.0
Dil: En iyi Fransızca performansı
```

## 🛠️ Kurulum Adımları

### Adım 1: Sistem Hazırlığı

```bash
# CUDA kurulumu
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install cuda-12-3

# Python environment
python3 -m venv /opt/netz-ai/venv
source /opt/netz-ai/venv/bin/activate
pip install --upgrade pip
```

### Adım 2: vLLM Kurulumu

```bash
# vLLM installation
pip install vllm==0.2.7
pip install ray==2.9.1  # Multi-GPU support

# Dependencies
pip install transformers accelerate sentencepiece protobuf
```

### Adım 3: Model İndirme

```python
# download_model.py
from huggingface_hub import snapshot_download
import os

# Model seçimi
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
LOCAL_DIR = "/opt/netz-ai/models/mistral-7b"

# Offline kullanım için model indirme
snapshot_download(
    repo_id=MODEL_ID,
    local_dir=LOCAL_DIR,
    local_dir_use_symlinks=False,
    resume_download=True,
    token="YOUR_HF_TOKEN"  # Gerekirse
)
```

### Adım 4: Model Optimizasyonu

```bash
# Quantization (Bellek optimizasyonu)
python -m vllm.entrypoints.openai.api_server \
    --model /opt/netz-ai/models/mistral-7b \
    --quantization awq \
    --dtype half \
    --max-model-len 8192
```

## 🔧 Fine-tuning Süreci

### 1. Veri Hazırlama
```python
# prepare_data.py
import json

training_data = []

# Şirket dokümanlarından örnekler
examples = [
    {
        "instruction": "Qu'est-ce que NETZ Informatique?",
        "input": "",
        "output": "NETZ Informatique est une société de services informatiques basée à Pontarlier..."
    },
    # Daha fazla örnek...
]

# JSONL formatında kaydet
with open('netz_training_data.jsonl', 'w') as f:
    for example in examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')
```

### 2. LoRA Fine-tuning
```bash
# LoRA adapter eğitimi
python finetune_lora.py \
    --base_model /opt/netz-ai/models/mistral-7b \
    --data_path ./netz_training_data.jsonl \
    --output_dir ./lora_adapters/netz_v1 \
    --num_epochs 3 \
    --learning_rate 2e-5 \
    --lora_r 16 \
    --lora_alpha 32
```

### 3. Model Merge
```python
# merge_adapter.py
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained(
    "/opt/netz-ai/models/mistral-7b"
)
model = PeftModel.from_pretrained(
    base_model, 
    "./lora_adapters/netz_v1"
)
model = model.merge_and_unload()
model.save_pretrained("/opt/netz-ai/models/mistral-7b-netz")
```

## 🚀 Production Deployment

### 1. vLLM Server Başlatma
```bash
# systemd service file: /etc/systemd/system/netz-llm.service
[Unit]
Description=NETZ AI LLM Server
After=network.target

[Service]
Type=simple
User=netz-ai
Group=netz-ai
WorkingDirectory=/opt/netz-ai
Environment="PATH=/opt/netz-ai/venv/bin"
ExecStart=/opt/netz-ai/venv/bin/python -m vllm.entrypoints.openai.api_server \
    --model /opt/netz-ai/models/mistral-7b-netz \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.9
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Multi-GPU Konfigürasyonu
```yaml
# vllm_config.yaml
model: /opt/netz-ai/models/mistral-7b-netz
tensor_parallel_size: 2  # 2 GPU kullanımı
pipeline_parallel_size: 1
max_num_batched_tokens: 8192
max_num_seqs: 256
trust_remote_code: true
```

## 📈 Performans Optimizasyonu

### 1. Caching Stratejisi
```python
# cache_config.py
from vllm import LLM, SamplingParams

# KV cache optimization
llm = LLM(
    model="/opt/netz-ai/models/mistral-7b-netz",
    gpu_memory_utilization=0.9,
    swap_space=4,  # GB
    cache_dtype="fp16"
)
```

### 2. Batch Processing
```python
# batch_inference.py
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
    presence_penalty=0.1,
    frequency_penalty=0.1
)

# Batch requests
prompts = ["Question 1", "Question 2", ...]
outputs = llm.generate(prompts, sampling_params)
```

## 🧪 Model Testing

### Test Script
```python
# test_model.py
import requests
import json

# Test API endpoint
url = "http://localhost:8000/v1/completions"

# Test prompts in French
test_prompts = [
    "Quelles sont les services de NETZ Informatique?",
    "Comment contacter le support technique?",
    "Quelle est la politique de sécurité?"
]

for prompt in test_prompts:
    response = requests.post(url, json={
        "model": "mistral-7b-netz",
        "prompt": f"[INST] {prompt} [/INST]",
        "max_tokens": 200,
        "temperature": 0.7
    })
    print(f"Q: {prompt}")
    print(f"A: {response.json()['choices'][0]['text']}\n")
```

## 📊 Monitoring ve Metrics

### Prometheus Metrics
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'vllm'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Key Metrics to Track
- Request latency (p50, p95, p99)
- Tokens per second
- GPU utilization
- Memory usage
- Queue depth

## 🔄 Model Güncelleme Stratejisi

### 1. A/B Testing
```python
# ab_test_config.py
models = {
    "stable": "/opt/netz-ai/models/mistral-7b-netz-v1",
    "canary": "/opt/netz-ai/models/mistral-7b-netz-v2"
}

traffic_split = {
    "stable": 0.9,  # %90 traffic
    "canary": 0.1   # %10 traffic
}
```

### 2. Rollback Plan
```bash
# rollback.sh
#!/bin/bash
CURRENT_MODEL="/opt/netz-ai/models/current"
PREVIOUS_MODEL="/opt/netz-ai/models/previous"

# Quick rollback
mv $CURRENT_MODEL $CURRENT_MODEL.failed
mv $PREVIOUS_MODEL $CURRENT_MODEL
systemctl restart netz-llm
```

---
*Son güncelleme: 2025-01-09*