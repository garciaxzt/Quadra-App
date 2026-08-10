from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st

from image_processing import process_image
from video_processing import process_video


st.set_page_config(page_title="Quadra — imagens e vídeos", page_icon="Q", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@500&family=Inter:wght@400;600;700;800&family=Playfair+Display:ital@1&display=swap');
    :root { --ink:#08080a; --paper:#dedee3; --surface:#f4f4f6; --purple:#7c3aed; --purple-dark:#5b21b6; --muted:#5f5f69; }
    .stApp { background:var(--paper); color:var(--ink); font-family:'Inter',sans-serif; }
    [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display:none; }
    .block-container { max-width:1040px; padding-top:1.3rem; padding-bottom:3rem; }
    .brandbar { display:flex; align-items:center; justify-content:space-between; padding:10px 0 22px; border-bottom:2px solid var(--ink); }
    .brand { display:flex; align-items:center; gap:10px; font-size:24px; font-weight:800; letter-spacing:-1px; }
    .mark { display:grid; place-items:center; width:32px; height:32px; border-radius:7px; background:var(--ink); color:#c4a7ff; font-family:'DM Mono'; font-size:16px; box-shadow:4px 4px 0 var(--purple); }
    .safe { color:#3f3f46; font-size:12px; font-weight:700; }
    .safe:before { content:''; display:inline-block; width:7px; height:7px; margin-right:8px; border-radius:50%; background:var(--purple); box-shadow:0 0 0 4px #d8c7ff; }
    .hero { text-align:center; padding:58px 15px 28px; }
    .eyebrow { color:var(--purple-dark); font:700 11px 'DM Mono'; letter-spacing:2px; }
    .hero h1 { margin:14px auto 18px; color:var(--ink); font-size:clamp(43px,7vw,74px); line-height:.98; letter-spacing:-4px; font-weight:800; }
    .hero h1 em { display:block; color:var(--purple); font-family:'Playfair Display',serif; font-weight:400; }
    .hero p { max-width:650px; margin:auto; color:var(--muted); line-height:1.6; }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap:10px; margin:0 0 22px; }
    [data-testid="stTabs"] button[role="tab"] { min-height:48px; padding:10px 24px; border:1px solid #a1a1aa; border-radius:10px; background:var(--surface); color:var(--ink); font-weight:800; }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] { background:var(--ink); color:white; border-color:var(--purple); box-shadow:4px 4px 0 var(--purple); }
    [data-testid="stFileUploader"] { padding:24px; border:2px dashed #71717a; border-radius:18px; background:var(--surface); box-shadow:8px 8px 0 rgba(8,8,10,.12); }
    [data-testid="stFileUploaderDropzone"] { background:#e9e9ed; border-color:#8b5cf6; }
    div[role="radiogroup"] { display:flex !important; flex-wrap:wrap !important; gap:8px; }
    div[role="radiogroup"] label { min-height:42px; padding:8px 14px; background:var(--surface); border:1px solid #a1a1aa; border-radius:9px; }
    div[role="radiogroup"] label:has(input:checked) { border-color:var(--purple); box-shadow:3px 3px 0 var(--purple); }
    div[role="radiogroup"] label p, div[role="radiogroup"] label span { color:var(--ink) !important; opacity:1 !important; visibility:visible !important; }
    .setting-card { margin:8px 0 5px; color:var(--muted); font-size:12px; }
    .upload-title { margin:18px 0 -42px 26px; position:relative; z-index:2; color:var(--ink); font-size:14px; font-weight:600; pointer-events:none; }
    .metric { color:var(--purple-dark); font-size:12px; font-weight:800; }
    .stDownloadButton button, .stButton button { width:100%; min-height:44px; border:0; border-radius:9px; background:var(--ink); color:white; font-weight:700; }
    .stDownloadButton button, .stButton button { box-shadow:4px 4px 0 var(--purple); }
    .stDownloadButton button:hover, .stButton button:hover { background:var(--purple-dark); color:white; border:0; }
    .video-note { margin:8px 0 15px; padding:12px 14px; border-left:4px solid var(--purple); border-radius:8px; background:#ddd2f8; color:#2e1065; font-size:13px; }
    @media(max-width:700px){
      .block-container{padding-left:16px;padding-right:16px}.safe{font-size:0}.safe:after{content:'Processamento seguro';font-size:11px}
      .hero{padding:38px 0 24px}.hero h1{letter-spacing:-3px}
      [data-testid="stTabs"] [data-baseweb="tab-list"]{display:grid;grid-template-columns:1fr 1fr;width:100%}
      [data-testid="stTabs"] button[role="tab"]{width:100%;padding:8px}
      div[role="radiogroup"]{flex-direction:column !important;align-items:stretch !important}
      div[role="radiogroup"] label{display:flex !important;width:100% !important;min-height:46px;align-items:center}
      div[role="radiogroup"] label p{display:block !important;white-space:normal !important;font-size:14px !important}
      [data-testid="stFileUploader"]{padding:24px 16px 16px}.upload-title{margin-left:18px}
    }
    </style>
    <div class="brandbar"><div class="brand"><span class="mark">Q</span>quadra</div><div class="safe">Processamento local e seguro</div></div>
    <section class="hero"><div class="eyebrow">CONVERSOR EM LOTE</div><h1>Suas mídias, <em>do seu jeito.</em></h1><p>Prepare imagens e vídeos nos formatos certos, sem cadastro.</p></section>
    """,
    unsafe_allow_html=True,
)


def image_tab() -> None:
    settings, background = st.columns([1.25, 1])
    with settings:
        st.markdown('<div class="setting-card">FORMATO DA IMAGEM</div>', unsafe_allow_html=True)
        format_label = st.radio("Formato da imagem", ["1:1 quadrado", "Tamanho original"], horizontal=True, label_visibility="collapsed")
    with background:
        st.markdown('<div class="setting-card">FUNDO</div>', unsafe_allow_html=True)
        white_background = st.toggle("Remover fundo e aplicar branco 100%", help="A primeira execução pode demorar um pouco mais.")

    st.markdown('<div class="upload-title">Solte suas imagens aqui</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Enviar imagens", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, label_visibility="collapsed", key="images")
    if len(uploaded_files) > 20:
        st.error("Selecione no máximo 20 imagens por vez.")
        uploaded_files = uploaded_files[:20]
    if not uploaded_files:
        return

    aspect_mode = "square" if format_label == "1:1 quadrado" else "original"
    signature = (tuple((f.name, f.size) for f in uploaded_files), aspect_mode, white_background)
    if st.session_state.get("image_signature") != signature:
        results = []
        progress = st.progress(0, text="Preparando suas imagens…")
        for index, uploaded in enumerate(uploaded_files, 1):
            try:
                output, dimensions = process_image(uploaded.getvalue(), aspect_mode=aspect_mode, remove_background=white_background)
                suffix = "quadrada" if aspect_mode == "square" else "original"
                results.append({"name": uploaded.name, "filename": f"{Path(uploaded.name).stem}-{suffix}.jpg", "data": output, "before": uploaded.size, "dimensions": dimensions})
            except Exception as exc:
                results.append({"name": uploaded.name, "error": str(exc)})
            progress.progress(index / len(uploaded_files), text=f"Processando {index} de {len(uploaded_files)}…")
        progress.empty()
        st.session_state.image_signature, st.session_state.image_results = signature, results

    results = st.session_state.get("image_results", [])
    successful = [item for item in results if not item.get("error")]
    if len(successful) > 1:
        archive = BytesIO()
        with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
            for item in successful:
                zip_file.writestr(item["filename"], item["data"])
        st.download_button("Baixar todas em ZIP", archive.getvalue(), "quadra-imagens.zip", "application/zip", use_container_width=True)
    columns = st.columns(3)
    for index, item in enumerate(results):
        with columns[index % 3]:
            if item.get("error"):
                st.error(f"{item['name']}: {item['error']}")
                continue
            st.image(item["data"], use_container_width=True)
            width, height = item["dimensions"]
            st.markdown(f"**{item['name']}**  \n<span class='metric'>{item['before']/1048576:.2f} MB → {len(item['data'])/1048576:.2f} MB · {width}×{height}px</span>", unsafe_allow_html=True)
            st.download_button("Baixar imagem", item["data"], item["filename"], "image/jpeg", key=f"image-download-{index}", use_container_width=True)


def video_tab() -> None:
    st.markdown('<div class="setting-card">FORMATO DO VÍDEO</div>', unsafe_allow_html=True)
    format_label = st.radio("Formato do vídeo", ["9:16 vertical", "16:9 horizontal"], horizontal=True, label_visibility="collapsed")
    st.markdown('<div class="video-note">O vídeo será recortado pelo centro e convertido para MP4, mantendo o áudio.</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-title">Solte seus vídeos aqui</div>', unsafe_allow_html=True)
    uploaded_videos = st.file_uploader("Enviar vídeos", type=["mp4", "mov", "avi", "mkv", "webm", "m4v"], accept_multiple_files=True, label_visibility="collapsed", key="videos")
    if len(uploaded_videos) > 5:
        st.error("Selecione no máximo 5 vídeos por vez.")
        uploaded_videos = uploaded_videos[:5]
    if not uploaded_videos:
        return

    aspect = "vertical" if format_label.startswith("9:16") else "horizontal"
    signature = (tuple((f.name, f.size) for f in uploaded_videos), aspect)
    if st.session_state.get("video_signature") != signature:
        results = []
        progress = st.progress(0, text="Preparando seus vídeos…")
        for index, uploaded in enumerate(uploaded_videos, 1):
            try:
                output = process_video(uploaded.getvalue(), uploaded.name, aspect)
                results.append({"name": uploaded.name, "filename": f"{Path(uploaded.name).stem}-{aspect}.mp4", "data": output, "before": uploaded.size})
            except Exception as exc:
                results.append({"name": uploaded.name, "error": str(exc)})
            progress.progress(index / len(uploaded_videos), text=f"Convertendo {index} de {len(uploaded_videos)}…")
        progress.empty()
        st.session_state.video_signature, st.session_state.video_results = signature, results

    for index, item in enumerate(st.session_state.get("video_results", [])):
        if item.get("error"):
            st.error(f"{item['name']}: {item['error']}")
            continue
        st.video(item["data"], format="video/mp4")
        st.markdown(f"**{item['name']}**  \n<span class='metric'>{item['before']/1048576:.2f} MB → {len(item['data'])/1048576:.2f} MB · MP4</span>", unsafe_allow_html=True)
        st.download_button("Baixar vídeo MP4", item["data"], item["filename"], "video/mp4", key=f"video-download-{index}", use_container_width=True)


images, videos = st.tabs(["🖼️ Imagens", "🎬 Vídeos"])
with images:
    image_tab()
with videos:
    video_tab()
