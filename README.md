# Kontakt Home - Zəng Keyfiyyəti Qiymətləndirmə Sistemi

Bu layihə müştəri xidməti transkriptlərini analiz edib `KR2.1` - `KR2.5` meyarları üzrə 0-3 arası skor verir.

## Niyə bu yanaşma?
Mən **hibrid pipeline** seçdim:
- Rule-based hissə: sürətli, izah edilə bilən, ucuz və sabitdir.
- LLM hissə (OpenRouter + `google/gemini-2.5-flash-lite`): daha nüanslı dil analizi üçün istifadə olunur.

Bu bölünmə həm xərci azaldır, həm də production mühitində nəzarəti artırır.

## Qovluq strukturu
- `src/kontakt_qc/engine.py` - əsas orkestrasiya
- `src/kontakt_qc/rules.py` - rule-based scoring
- `src/kontakt_qc/llm_client.py` - OpenRouter inteqrasiyası
- `src/kontakt_qc/prompts.py` - prompt idarəetməsi
- `src/kontakt_qc/evaluation.py` - eval dataset metrikləri
- `tests/` - unit testlər

## Quraşdırma
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment dəyişənləri
`.env.example` faylını `.env` kimi kopyalayın:
```bash
cp .env.example .env
```

Doldurun:
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL=google/gemini-2.5-flash-lite`

## İstifadə
Tək zəng üçün:
```bash
PYTHONPATH=src python main.py evaluate --input sample_input.json
```

Dataset üzrə qiymətləndirmə:
```bash
PYTHONPATH=src python main.py eval-dataset --dataset "Task_1_Eval_dataset(1).json"
```

## Rule-based vs LLM qərarı necə verilir?
- Data validasiyası və edge-case yoxlamaları əvvəlcə rule-based ilə edilir.
- Audio/transkript çox qısadırsa (`<0.1s`) LLM çağırılmır.
- API key yoxdursa və ya LLM xətası varsa sistem rule-based fallback verir.
- LLM dəlili transkriptdə tapılmırsa (hallucination), həmin LLM skoru nəzərə alınmır.

## Robustluq və edge-case-lər
- Boş/qırıq payload üçün explicit error cavabı qaytarılır.
- PII maskalama (`kart`, `telefon`) LLM-ə göndərməzdən əvvəl tətbiq olunur.
- Logging `print` əvəzinə `logging` ilə aparılır.

## Testlər
```bash
PYTHONPATH=src pytest
```

## Docker
```bash
docker compose up --build
```

## CI/CD
`.github/workflows/ci.yml` daxilində push/pull_request zamanı testlər avtomatik işə düşür.

## Qarşılaşılan çətinliklər və həll
- Meyar mətnləri subyektivdir: əvvəl rule-ları izah edilə bilən saxladım, sonra LLM ilə yumşaq blend etdim.
- Hallucination riski: LLM evidence-in transkriptdə varlığını məcburi yoxladım.
- Real data xaosu: validasiya qatını sərtləşdirdim və fail-safe fallback əlavə etdim.

## Təkmilləşdirmə imkanları
- Daha güclü semantik matching (embedding-based evidence grounding)
- Confusion matrix və meyar üzrə threshold tuning
- FastAPI endpoint + observability (Prometheus/Grafana)
