import json
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from libs.flash_stm32 import flash_stm32_f4xx

api_router = APIRouter()


@api_router.post("/flash")
async def flash_elf_file(file: UploadFile = File(...)):
    """
    ELFファイルを受け取り、STM32F4xxに書き込む

    Args:
        file: 書き込むELFファイル

    Returns:
        StreamingResponse: 書き込み処理のログをリアルタイムで返す
    """
    if not file.filename or not file.filename.endswith(".elf"):
        raise HTTPException(status_code=400, detail="file type must be ELF (.elf)")

    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"temp_{file.filename}")

    with open(temp_file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

        print(f"saving to temporary file: {temp_file_path}")

    def log_generator():
        try:
            flash_gen = flash_stm32_f4xx(temp_file_path)
            success = False
            while True:
                try:
                    log_message = next(flash_gen)
                    print(log_message)
                    yield json.dumps(
                        {
                            "type": "log",
                            "message": log_message,
                        },
                        ensure_ascii=False,
                    ) + "\n"
                except StopIteration as e:
                    success = e.value if e.value is not None else False
                    break

            print(f"final success: {success}")
            yield json.dumps(
                {
                    "type": "complete",
                    "success": success,
                    "message": "書き込み完了" if success else "書き込み失敗",
                },
                ensure_ascii=False,
            ) + "\n"

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print(f"removed temporary file: {temp_file_path}")

    return StreamingResponse(
        log_generator(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
