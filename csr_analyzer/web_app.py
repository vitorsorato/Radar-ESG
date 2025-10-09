from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from typing import List
from pathlib import Path
import shutil
import zipfile
import re

from .pdf_sentiment_processor import PDFSentimentProcessor
from .pdf_utils import extract_text_from_pdf


app = FastAPI(title="CSR Analyzer - Web")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Envio de PDFs - Análise de Sentimento</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
    .container { max-width: 760px; margin: 0 auto; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; }
    h1 { margin: 0 0 1rem; font-size: 1.5rem; }
    button { background: #111827; color: white; border: 0; padding: 0.75rem 1rem; border-radius: 8px; cursor: pointer; }
    button:hover { background: #374151; }
    .muted { color: #6b7280; font-size: 0.9rem; }
    .field { margin: 0.75rem 0; }
    .row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .spinner { width: 16px; height: 16px; border: 2px solid #e5e7eb; border-top-color: #111827; border-radius: 50%; animation: spin 0.8s linear infinite; display: none; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .progress { height: 8px; background: #e5e7eb; border-radius: 9999px; overflow: hidden; display: none; }
    .bar { height: 100%; width: 0%; background: #10b981; transition: width .2s ease; }
    .progress-text { display:none; font-size: 0.9rem; color: #374151; }
    .actions { display: none; gap: 8px; }
    a.button { text-decoration: none; color: white; background: #2563eb; padding: 0.5rem .8rem; border-radius: 8px; }
    /* Pretty file button */
    .btn { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; border: 0; border-radius: 12px; padding: 0.9rem 1.25rem; font-size: 1rem; transition: all .15s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .btn-primary { background: #eef2ff; color: #1f2937; border: 1px solid #e5e7eb; }
    .btn-primary:hover { background: #e0e7ff; box-shadow: 0 2px 6px rgba(0,0,0,0.07); }
    .btn-primary:active { transform: translateY(1px); }
    .btn .icon { width: 18px; height: 18px; display: inline-block; }
  </style>
  <script>
    async function submitForm(e) {
      e.preventDefault();
      const form = document.getElementById('upload-form');
      const files = form.querySelector('input[name="files"]').files;
      if (!files.length) { alert('Selecione ao menos um arquivo.'); return; }
      const data = new FormData(form);

      // Tamanho total dos arquivos em MB
      const totalBytes = Array.from(files).reduce((sum, f) => sum + (f.size || 0), 0);
      const totalMB = (totalBytes / (1024*1024)).toFixed(2);

      // UI feedback
      document.getElementById('spinner').style.display = 'inline-block';
      document.getElementById('progress').style.display = 'block';
      document.getElementById('bar').style.width = '5%';
      const ptext = document.getElementById('progress-text');
      ptext.style.display = 'inline-block';
      document.getElementById('actions').style.display = 'none';
      document.getElementById('result').textContent = 'Enviando e processando ' + files.length + ' arquivo(s) — ' + totalMB + ' MB';

      try {
        const json = await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', '/analyze');
          xhr.responseType = 'json';
          xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
              const uploadedMB = (e.loaded / (1024*1024)).toFixed(2);
              const percent = Math.min(95, Math.max(10, Math.round((e.loaded / e.total) * 80)));
              document.getElementById('bar').style.width = percent + '%';
              ptext.textContent = `Upload: ${uploadedMB} / ${totalMB} MB`;
            }
          };
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(xhr.response);
            } else {
              reject(new Error('Falha na análise'));
            }
          };
          xhr.onerror = () => reject(new Error('Erro de rede'));
          xhr.send(data);
        });
        document.getElementById('bar').style.width = '100%';
        ptext.textContent = 'Processamento concluído';

        const pre = document.getElementById('result');
        pre.textContent = JSON.stringify(json, null, 2);

        // Mostrar botões de download
        const actions = document.getElementById('actions');
        actions.style.display = 'flex';
        const geral = document.getElementById('btn-geral');
        const zip = document.getElementById('btn-zip');
        geral.href = json.downloads.resultado_geral;
        zip.href = json.downloads.zip;

        // Auto download se marcado
        const auto = document.getElementById('auto');
        if (auto.checked) {
          const a1 = document.createElement('a'); a1.href = geral.href; a1.download = '';
          document.body.appendChild(a1); a1.click(); a1.remove();
          const a2 = document.createElement('a'); a2.href = zip.href; a2.download = '';
          document.body.appendChild(a2); a2.click(); a2.remove();
        }
      } catch (err) {
        document.getElementById('result').textContent = 'Erro: ' + err.message;
      } finally {
        document.getElementById('spinner').style.display = 'none';
        setTimeout(() => { document.getElementById('progress').style.display = 'none'; document.getElementById('bar').style.width = '0%'; ptext.style.display = 'none'; ptext.textContent=''; }, 800);
      }
    }
    // Atualiza contador de arquivos (após DOM pronto)
    window.addEventListener('DOMContentLoaded', () => {
      const fileInput = document.getElementById('file-input');
      const fileCount = document.getElementById('file-count');
      if (!fileInput || !fileCount) return;
      const update = () => {
        const n = fileInput.files ? fileInput.files.length : 0;
        fileCount.textContent = n ? `${n} arquivo(s) selecionado(s)` : 'Nenhum arquivo selecionado';
      };
      fileInput.addEventListener('change', update);
    });
    
    // ======== FOG (legibilidade) ========
    async function submitFog(e) {
      e.preventDefault();
      const form = document.getElementById('fog-form');
      const files = form.querySelector('input[name="files"]').files;
      if (!files.length) { alert('Selecione ao menos um arquivo.'); return; }
      const data = new FormData(form);

      const totalBytes = Array.from(files).reduce((s, f) => s + (f.size||0), 0);
      const totalMB = (totalBytes / (1024*1024)).toFixed(2);

      document.getElementById('fog-spinner').style.display = 'inline-block';
      document.getElementById('fog-progress').style.display = 'block';
      document.getElementById('fog-bar').style.width = '5%';
      const fptext = document.getElementById('fog-progress-text');
      fptext.style.display = 'inline-block';
      document.getElementById('fog-actions').style.display = 'none';
      document.getElementById('fog-result').textContent = 'Enviando e processando ' + files.length + ' arquivo(s) — ' + totalMB + ' MB';

      try {
        const json = await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', '/analyze-fog');
          xhr.responseType = 'json';
          xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
              const uploadedMB = (e.loaded / (1024*1024)).toFixed(2);
              const percent = Math.min(95, Math.max(10, Math.round((e.loaded / e.total) * 80)));
              document.getElementById('fog-bar').style.width = percent + '%';
              fptext.textContent = `Upload: ${uploadedMB} / ${totalMB} MB`;
            }
          };
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(xhr.response);
            } else {
              reject(new Error('Falha no cálculo'));
            }
          };
          xhr.onerror = () => reject(new Error('Erro de rede'));
          xhr.send(data);
        });
        document.getElementById('fog-bar').style.width = '100%';
        fptext.textContent = 'Concluído';

        const pre = document.getElementById('fog-result');
        pre.textContent = JSON.stringify(json, null, 2);

        const actions = document.getElementById('fog-actions');
        actions.style.display = 'flex';
        const fogcsv = document.getElementById('btn-fog-csv');
        fogcsv.href = json.downloads.csv;

        if (document.getElementById('fog-auto').checked) {
          const a = document.createElement('a'); a.href = fogcsv.href; a.download = ''; document.body.appendChild(a); a.click(); a.remove();
        }
      } catch (err) {
        document.getElementById('fog-result').textContent = 'Erro: ' + err.message;
      } finally {
        document.getElementById('fog-spinner').style.display = 'none';
        setTimeout(() => { document.getElementById('fog-progress').style.display = 'none'; document.getElementById('fog-bar').style.width = '0%'; fptext.style.display = 'none'; fptext.textContent=''; }, 800);
      }
    }
    // contador FOG
    window.addEventListener('DOMContentLoaded', () => {
      const input = document.getElementById('fog-file-input');
      const label = document.getElementById('fog-file-count');
      if (!input || !label) return;
      const update = () => {
        const n = input.files ? input.files.length : 0;
        label.textContent = n ? `${n} arquivo(s) selecionado(s)` : 'Nenhum arquivo selecionado';
      };
      input.addEventListener('change', update);
    });
  </script>
  </head>
<body>
  <div class=\"container\">
    <div class=\"card\">
      <h1>Envie PDFs para análise</h1>
      <p class=\"muted\">Envie um ou mais PDFs. Geramos o \"resultado_geral.csv\" e um pacote ZIP com as pastas individuais.</p>
      <form id=\"upload-form\" onsubmit=\"submitForm(event)\"> 
        <div class=\"field\"> 
          <label for=\"file-input\" class=\"btn btn-primary\">
            <svg class=\"icon\" viewBox=\"0 0 24 24\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M12 16V4m0 12l-3.5-3.5M12 16l3.5-3.5M6 20h12\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>
            Escolher arquivos
          </label>
          <input id=\"file-input\" type=\"file\" name=\"files\" accept=\"application/pdf,text/plain\" multiple required style=\"display:none\" />
          <span id=\"file-count\" class=\"muted\" style=\"margin-left:10px\">Nenhum arquivo selecionado</span>
        </div>
        <div class=\"row\">
          <label class=\"muted\"><input type=\"checkbox\" id=\"auto\" checked /> Baixar arquivos automaticamente</label>
          <span id=\"spinner\" class=\"spinner\"></span>
          <div id=\"progress\" class=\"progress\" style=\"flex:1\"><div id=\"bar\" class=\"bar\"></div></div>
          <span id=\"progress-text\" class=\"progress-text\"></span>
          <button type=\"submit\">Analisar</button>
        </div>
      </form>
      <div id=\"actions\" class=\"actions\" style=\"margin-top:12px\"> 
        <a id=\"btn-geral\" class=\"button\" href=\"#\">Baixar resultado_geral.csv</a>
        <a id=\"btn-zip\" class=\"button\" href=\"#\">Baixar ZIP dos resultados</a>
      </div>
      <pre id=\"result\" style=\"margin-top:1rem; background:#f9fafb; padding:1rem; border-radius:8px; overflow:auto; max-height:300px;\"></pre>
    </div>
    <div class=\"card\" style=\"margin-top:20px\"> 
      <h1>Índice Gunning Fog (legibilidade)</h1>
      <p class=\"muted\">Envie PDFs ou TXTs. Calculamos palavras, sentenças, palavras complexas (≥3 sílabas) e o índice Fog.</p>
      <form id=\"fog-form\" onsubmit=\"submitFog(event)\"> 
        <div class=\"field\"> 
          <label for=\"fog-file-input\" class=\"btn btn-primary\">
            <svg class=\"icon\" viewBox=\"0 0 24 24\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M12 16V4m0 12l-3.5-3.5M12 16l3.5-3.5M6 20h12\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>
            Escolher arquivos
          </label>
          <input id=\"fog-file-input\" type=\"file\" name=\"files\" accept=\"application/pdf,text/plain\" multiple required style=\"display:none\" />
          <span id=\"fog-file-count\" class=\"muted\" style=\"margin-left:10px\">Nenhum arquivo selecionado</span>
        </div>
        <div class=\"row\"> 
          <label class=\"muted\"><input type=\"checkbox\" id=\"fog-auto\" checked /> Baixar CSV automaticamente</label>
          <span id=\"fog-spinner\" class=\"spinner\"></span>
          <div id=\"fog-progress\" class=\"progress\" style=\"flex:1\"><div id=\"fog-bar\" class=\"bar\"></div></div>
          <span id=\"fog-progress-text\" class=\"progress-text\"></span>
          <button type=\"submit\">Calcular Fog</button>
        </div>
      </form>
      <div id=\"fog-actions\" class=\"actions\" style=\"margin-top:12px\"> 
        <a id=\"btn-fog-csv\" class=\"button\" href=\"#\">Baixar fog_resultados.csv</a>
      </div>
      <pre id=\"fog-result\" style=\"margin-top:1rem; background:#f9fafb; padding:1rem; border-radius:8px; overflow:auto; max-height:300px;\"></pre>
    </div>
  </div>
</body>
</html>
"""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(files: List[UploadFile] = File(...)):
    # Salva uploads em uma pasta temporária dentro de outputs/uploads
    uploads_root = Path("outputs/uploads")
    _ensure_dir(uploads_root)
    temp_dir = uploads_root / "session"
    # Limpa pasta de sessão
    if temp_dir.exists():
        for p in temp_dir.rglob("*"):
            if p.is_file():
                p.unlink(missing_ok=True)
    _ensure_dir(temp_dir)

    saved_paths = []
    for f in files:
        dest = temp_dir / f.filename
        with dest.open("wb") as w:
            shutil.copyfileobj(f.file, w)
        saved_paths.append(str(dest))

    # Processa com o PDFSentimentProcessor
    processor = PDFSentimentProcessor()
    results = []
    for path in saved_paths:
        results.append(processor.process_pdf(path))

    summary = processor.generate_report_summary(results)
    out_dir = Path("outputs")
    _ensure_dir(out_dir)
    # Limpa a pasta de saída (mantém uploads)
    for child in out_dir.iterdir():
        if child.name == "uploads":
            continue
        if child.is_file():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
    processor.save_results(results, output_dir=str(out_dir))

    # Cria ZIP consolidado com resultados
    zip_path = out_dir / "analise_resultados.zip"
    if zip_path.exists():
        zip_path.unlink(missing_ok=True)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        geral = out_dir / "resultado_geral.csv"
        if geral.exists():
            zf.write(geral, arcname="resultado_geral.csv")
        for child in out_dir.iterdir():
            if child.is_dir():
                for p in child.rglob('*'):
                    if p.is_file():
                        zf.write(p, arcname=str(p.relative_to(out_dir)))

    return JSONResponse({
        "total_files": summary.get("total_files", 0),
        "avg_positive": summary.get("avg_positive", 0.0),
        "avg_negative": summary.get("avg_negative", 0.0),
        "output_dir": str(out_dir),
        "downloads": {
            "resultado_geral": f"/download/resultado_geral.csv?output_dir={out_dir}",
            "zip": f"/download/analise_resultados.zip?output_dir={out_dir}"
        },
        "message": "Análise concluída. Arquivos prontos para download."
    })


def _tokenize_words(text: str) -> List[str]:
    return re.findall(r"[\wÀ-ÖØ-öø-ÿ]+", text, flags=re.UNICODE)


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"[\.!?]+\s*", text)
    return [p for p in parts if p.strip()]


def _count_syllables(word: str) -> int:
    # Heurística simples baseada em grupos de vogais (pt-BR)
    w = word.lower()
    groups = re.findall(r"[aeiouáéíóúâêôãõü]+", w)
    return max(1, len(groups))


def _compute_fog_index(words: int, sentences: int, tokens: List[str]) -> float:
    if sentences == 0 or words == 0:
        return 0.0
    complex_words = sum(1 for w in tokens if _count_syllables(w) >= 3)
    avg_words_per_sentence = words / sentences
    percent_complex = (complex_words / words) * 100
    return 0.4 * (avg_words_per_sentence + percent_complex)


@app.post("/analyze-fog")
async def analyze_fog(files: List[UploadFile] = File(...)):
    uploads_root = Path("outputs/uploads")
    _ensure_dir(uploads_root)
    temp_dir = uploads_root / "fog_session"
    if temp_dir.exists():
        for p in temp_dir.rglob("*"):
            if p.is_file():
                p.unlink(missing_ok=True)
    _ensure_dir(temp_dir)

    saved_paths = []
    for f in files:
        dest = temp_dir / f.filename
        with dest.open("wb") as w:
            shutil.copyfileobj(f.file, w)
        saved_paths.append(dest)

    rows = []
    for path in saved_paths:
        text = ""
        pstr = str(path).lower()
        if pstr.endswith(".txt"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
        elif pstr.endswith(".pdf"):
            text = extract_text_from_pdf(str(path))
        tokens = _tokenize_words(text)
        sentences = len(_split_sentences(text))
        words = len(tokens)
        fog = _compute_fog_index(words, sentences, tokens)
        complex_words = sum(1 for w in tokens if _count_syllables(w) >= 3)
        rows.append({
            "arquivo": path.name,
            "palavras": words,
            "sentencas": sentences,
            "palavras_complexas": complex_words,
            "fog_index": round(fog, 2)
        })

    # Salva CSV consolidado
    out_dir = Path("outputs")
    _ensure_dir(out_dir)
    fog_csv = out_dir / "fog_resultados.csv"
    try:
        import csv
        with fog_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Arquivo", "Palavras", "Sentencas", "Palavras_Complexas", "Fog_Index"]) 
            for r in rows:
                w.writerow([r["arquivo"], r["palavras"], r["sentencas"], r["palavras_complexas"], f"{r['fog_index']:.2f}"])
    except Exception:
        pass

    return JSONResponse({
        "total_files": len(rows),
        "results": rows,
        "downloads": {
            "csv": f"/download/fog_resultados.csv?output_dir={out_dir}"
        }
    })

@app.get("/download/{filename}")
def download_file(filename: str, output_dir: str = "outputs"):
    allowed = {"resultado_geral.csv", "analise_resultados.zip", "fog_resultados.csv"}
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Arquivo não permitido")
    base = Path(output_dir)
    path = (base / filename).resolve()
    try:
        path.relative_to(base.resolve())
    except Exception:
        raise HTTPException(status_code=400, detail="Caminho inválido")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(path)


