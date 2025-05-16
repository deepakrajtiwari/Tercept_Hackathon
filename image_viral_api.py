from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import tempfile
import os
import uvicorn

from image_viral import generate_response  # Your updated function

app = FastAPI()

@app.post("/generate-caption/")
async def generate_caption(
    image: UploadFile = File(...),
    company_name: str = Form(...)
):
    try:
        suffix = os.path.splitext(image.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(image.file, tmp)
            temp_file_path = tmp.name

        result = generate_response(temp_file_path, company_name)

        os.remove(temp_file_path)

        # Return the structured response directly under 'result' key
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("image_viral_api:app", host="0.0.0.0", port=8000, reload=True)