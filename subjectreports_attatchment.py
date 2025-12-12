contents = [base_prompt]

# 1) 파일 업로더에서 온 이미지/PDF
if uploaded_files:
    for f in uploaded_files:
        file_bytes = f.getvalue()
        if f.type.startswith("image/"):
            contents.append({
                "mime_type": f.type,
                "data": file_bytes,
            })
        elif f.type == "application/pdf":
            contents.append({
                "mime_type": "application/pdf",
                "data": file_bytes,
            })

# 2) 클립보드(Ctrl+V)에서 온 이미지
if pasted_image is not None:
    # pasted_image 는 PIL.Image 이므로, 바이트로 변환
    buf = io.BytesIO()
    pasted_image.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    contents.append({
        "mime_type": "image/png",
        "data": img_bytes,
    })
