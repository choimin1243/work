from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
import openpyxl
from io import BytesIO
from urllib.parse import quote

app = FastAPI()

# index.html 파일을 웹 루트에 위치하도록 설정
html_file_path = Path(__file__).parent / "index.html"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return html_file_path.read_text()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 업로드된 파일을 메모리에 저장
        uploaded_file = file.file.read()

        # 엑셀 파일 열기
        wb = openpyxl.load_workbook(BytesIO(uploaded_file))
        sheet = wb.active

        # A1 셀에 값을 1로 변경
        sheet["A1"] = 1

        # 업데이트된 파일을 메모리에 저장
        updated_file_content = BytesIO()
        wb.save(updated_file_content)

        encoded_file_name = quote(file.filename, safe="")  # 파일 이름을 URL로 인코딩

        return StreamingResponse(
            iter([updated_file_content.getvalue()]),
            headers={
                "Content-Disposition": f"attachment; filename={encoded_file_name}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
