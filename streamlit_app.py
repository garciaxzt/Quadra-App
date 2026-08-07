from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st

from image_processing import MAX_BYTES, process_image


st.set_page_config(
    page_title="Quadra — imagens do seu jeito",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@500&family=Inter:wght@400;600;700;800&family=Playfair+Display:ital@1&display=swap');
    :root { --ink:#172026; --paper:#f7f5f0; --lime:#cbf36a; --olive:#799d34; --muted:#657077; }
    .stApp { background:var(--paper); color:var(--ink); font-family:'Inter',sans-serif; }
    [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display:none; }
    .block-container { max-width:1040px; padding-top:1.3rem; padding-bottom:3rem; }
    .brandbar { display:flex; align-items:center; justify-content:space-between; padding:10px 0 22px; border-bottom:1px solid #d9ded8; }
    .brand { display:flex; align-items:center; gap:10px; font-size:24px; font-weight:800; letter-spacing:-1px; }
    .mark { display:grid; place-items:center; width:32px; height:32px; border-radius:7px; background:var(--ink); color:var(--lime); font-family:'DM Mono'; font-size:16px; }
    .safe { color:#516056; font-size:12px; font-weight:600; }
    .safe:before { content:''; display:inline-block; width:7px; height:7px; margin-right:8px; border-radius:50%; background:#6eb32b; box-shadow:0 0 0 4px #dff0cc; }
    .hero { text-align:center; padding:64px 15px 34px; }
    .eyebrow { color:#64725e; font:700 11px 'DM Mono'; letter-spacing:2px; }
    .hero h1 { margin:14px auto 18px; color:var(--ink); font-size:clamp(45px,7vw,76px); line-height:.98; letter-spacing:-4px; font-weight:800; }
    .hero h1 em { display:block; color:var(--olive); font-family:'Playfair Display',serif; font-weight:400; }
    .hero p { max-width:650px; margin:auto; color:var(--muted); line-height:1.6; }
    [data-testid="stFileUploader"] { padding:24px; border:1px dashed #aeb8ab; border-radius:18px; background:white; box-shadow:0 20px 55px rgba(39,52,35,.07); }
    [data-testid="stFileUploaderDropzone"] { background:#fbfcf9; border-color:#c9d0c6; }
    div[data-testid="stRadio"] > label, div[data-testid="stToggle"] label { font-weight:700; color:var(--ink); }
    div[role="radiogroup"] { gap:8px; }
    div[role="radiogroup"] label { padding:8px 14px; background:white; border:1px solid #d9ded8; border-radius:9px; }
    .setting-card { margin-bottom:4px; color:var(--muted); font-size:12px; }
    .result-card { padding:12px; background:white; border:1px solid #d9ded8; border-radius:13px; }
    .metric { color:var(--olive); font-size:12px; font-weight:700; }
    .stDownloadButton button, .stButton button { width:100%; min-height:44px; border:0; border-radius:9px; background:var(--ink); color:white; font-weight:700; }
    .stDownloadButton button:hover, .stButton button:hover { background:#29383f; color:white; border:0; }
    .steps { display:grid; grid-template-columns:repeat(3,1fr); margin-top:65px; border-top:1px solid #d9ded8; }
    .step { padding:30px; border-right:1px solid #d9ded8; }
    .step:last-child { border:0; }
    .step b { color:#83a943; font:600 11px 'DM Mono'; }
    .step h3 { margin:10px 0 7px; font-size:17px; }
    .step p { margin:0; color:var(--muted); font-size:12px; line-height:1.55; }
    @media(max-width:700px){ .safe{font-size:0}.safe:after{content:'Processamento seguro';font-size:11px}.hero{padding-top:45px}.hero h1{letter-spacing:-3px}.steps{grid-template-columns:1fr}.step{border-right:0;border-bottom:1px solid #d9ded8;padding:22px 8px} }
    </style>
    <div class="brandbar">
      <div class="brand"><span class="mark">Q</span>quadra</div>
      <div class="safe">Processamento local e seguro</div>
    </div>
    <section class="hero">
      <div class="eyebrow">REDIMENSIONADOR EM LOTE</div>
      <h1>Suas imagens, <em>do seu jeito.</em></h1>
      <p>Envie várias fotos, escolha o formato e receba arquivos com menos de 2 MB. Sem cadastro.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

settings, background = st.columns([1.25, 1])
with settings:
    st.markdown('<div class="setting-card">FORMATO DA IMAGEM</div>', unsafe_allow_html=True)
    format_label = st.radio(
        "Formato da imagem",
        ["1:1 quadrado", "Tamanho original"],
        horizontal=True,
        label_visibility="collapsed",
    )
with background:
    st.markdown('<div class="setting-card">FUNDO</div>', unsafe_allow_html=True)
    white_background = st.toggle(
        "Remover fundo e aplicar branco 100%",
        help="Usa inteligência artificial. A primeira execução pode demorar um pouco mais.",
    )

uploaded_files = st.file_uploader(
    "Solte suas imagens aqui",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    help="Selecione até 20 imagens.",
)

if len(uploaded_files) > 20:
    st.error("Selecione no máximo 20 imagens por vez.")
    uploaded_files = uploaded_files[:20]

if uploaded_files:
    aspect_mode = "square" if format_label == "1:1 quadrado" else "original"
    signature = (
        tuple((file.name, file.size) for file in uploaded_files),
        aspect_mode,
        white_background,
    )

    if st.session_state.get("signature") != signature:
        results = []
        progress = st.progress(0, text="Preparando suas imagens…")
        for index, uploaded in enumerate(uploaded_files, start=1):
            try:
                output, dimensions = process_image(
                    uploaded.getvalue(),
                    aspect_mode=aspect_mode,
                    remove_background=white_background,
                )
                suffix = "quadrada" if aspect_mode == "square" else "original"
                filename = f"{Path(uploaded.name).stem}-{suffix}.jpg"
                results.append(
                    {
                        "name": uploaded.name,
                        "filename": filename,
                        "data": output,
                        "before": uploaded.size,
                        "after": len(output),
                        "dimensions": dimensions,
                        "error": None,
                    }
                )
            except Exception as exc:
                results.append({"name": uploaded.name, "error": str(exc)})
            progress.progress(index / len(uploaded_files), text=f"Processando {index} de {len(uploaded_files)}…")
        progress.empty()
        st.session_state.signature = signature
        st.session_state.results = results

    results = st.session_state.get("results", [])
    successful = [item for item in results if not item.get("error")]

    if len(successful) > 1:
        archive = BytesIO()
        with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
            for item in successful:
                zip_file.writestr(item["filename"], item["data"])
        st.download_button(
            "Baixar todas em ZIP",
            archive.getvalue(),
            "quadra-imagens.zip",
            "application/zip",
            use_container_width=True,
        )

    columns = st.columns(3)
    for index, item in enumerate(results):
        with columns[index % 3]:
            if item.get("error"):
                st.error(f"{item['name']}: {item['error']}")
                continue
            st.image(item["data"], use_container_width=True)
            width, height = item["dimensions"]
            st.markdown(
                f"**{item['name']}**  \n"
                f'<span class="metric">{item["before"] / 1024 / 1024:.2f} MB → {item["after"] / 1024 / 1024:.2f} MB · {width}×{height}px</span>',
                unsafe_allow_html=True,
            )
            st.download_button(
                "Baixar imagem",
                item["data"],
                item["filename"],
                "image/jpeg",
                key=f"download-{index}-{item['filename']}",
                use_container_width=True,
            )

st.markdown(
    """
    <section class="steps">
      <div class="step"><b>01</b><h3>Envie em lote</h3><p>Selecione imagens JPG, PNG ou WebP.</p></div>
      <div class="step"><b>02</b><h3>Personalize</h3><p>Escolha 1:1, original e o fundo branco opcional.</p></div>
      <div class="step"><b>03</b><h3>Baixe</h3><p>Salve individualmente ou todas em um ZIP.</p></div>
    </section>
    """,
    unsafe_allow_html=True,
)
