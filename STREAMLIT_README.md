# Quadra em Streamlit

Aplicativo para processar imagens em lote com Streamlit e Pillow.

## Recursos

- Upload de até 20 imagens JPG, PNG ou WebP.
- Saída quadrada 1:1 ou com as dimensões originais.
- Compressão automática para menos de 2 MB.
- Remoção opcional do fundo com aplicação de branco 100%.
- Download individual ou de todas as imagens em um arquivo ZIP.

## Executar

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

O app será aberto normalmente em `http://localhost:8501`.

## Publicação

O projeto está pronto para Streamlit Community Cloud, Render ou outro serviço compatível com Python. Use `streamlit_app.py` como arquivo principal.
