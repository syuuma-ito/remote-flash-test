import subprocess
import time
from pathlib import Path
from typing import Generator, Optional


def flash_stm32_f4xx(
    elf_path: str, openocd_path: Optional[str] = None
) -> Generator[str, None, bool]:
    """
    OpenOCDを使ってSTM32 F4xxにELFファイルを書き込む

    Args:
        elf_path (str): 書き込むELFファイルのパス
        openocd_path (str, optional): OpenOCDの実行ファイルパス。Noneの場合はPATHから検索

    Yields:
        str: ログ

    Returns:
        bool: 書き込み成功時はTrue、失敗時はFalse

    Raises:
        FileNotFoundError: ファイルが見つからない場合やOpenOCDが見つからない場合
    """

    elf_file = Path(elf_path)
    if not elf_file.exists():
        raise FileNotFoundError(f"ELF file not found: {elf_path}")

    if openocd_path is None:
        openocd_cmd = "openocd"
    else:
        openocd_cmd = openocd_path
        if not Path(openocd_path).exists():
            raise FileNotFoundError(f"OpenOCD not found: {openocd_path}")

    # STM32 F446用の設定ファイル
    openocd_config = ["-f", "interface/stlink.cfg", "-f", "target/stm32f4x.cfg"]

    normalized_path = str(elf_file.absolute()).replace("\\", "/")

    openocd_commands = [
        "init",
        "reset",
        "halt",
        f"flash write_image erase {normalized_path}",
        f"verify_image {normalized_path}",
        "reset",
        "exit",
    ]

    command_string = "; ".join(openocd_commands)
    cmd = [openocd_cmd] + openocd_config + ["-c", command_string]

    yield f"RUN: {' '.join(cmd)}"

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        while True:
            line = process.stdout.readline()
            if line == "" and process.poll() is not None:
                break

            if line:
                line = line.strip()
                if line:
                    yield f"OpenOCD: {line}"

        return_code = process.wait()

    except Exception as e:
        yield f"Error occurred while running OpenOCD: {e}"
        return False

    if return_code == 0:
        yield "Flashing completed successfully!"
        return True
    else:
        yield f"Flashing failed with return code: {return_code}"
        return False


def test_flash_elf():
    current_dir = Path(__file__).parent.parent.parent
    test_elf_path = current_dir / "test.elf"

    flash_generator = flash_stm32_f4xx(test_elf_path)
    result = False

    while True:
        try:
            log_message = next(flash_generator)
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            print(f"[{timestamp}] {log_message}")
        except StopIteration as e:
            result = e.value if e.value is not None else False
            break

    print(f"Flash result: {'Success' if result else 'Failed'}")
    return result


if __name__ == "__main__":
    test_flash_elf()
