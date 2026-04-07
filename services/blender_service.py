# services/blender_service.py — пример исправления
import subprocess
import logging
import tempfile
import os


class BlenderService:
    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or self._detect_blender()
        self.logger = logging.getLogger("BlenderService")

    def _detect_blender(self) -> str:
        """Авто-детект пути к Blender на Windows/Linux"""
        if os.name == "nt":
            # Проверка стандартных путей на Windows
            candidates = [
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                os.path.expandvars(r"%PROGRAMFILES%\Blender Foundation\*\blender.exe"),
            ]
            for path in candidates:
                if os.path.exists(path):
                    return path
        # Fallback: попробовать вызвать 'blender' из PATH
        return "blender"

    def execute_code(self, code: str, output_path: str = None) -> dict:
        """
        Выполняет Python-код в Blender и возвращает результат.
        """
        # Создаём временный файл с кодом
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            script_path = f.name

        try:
            # Формируем команду запуска
            cmd = [
                self.blender_path,
                "--background",  # Headless mode
                "--factory-startup",  # Чистый запуск без пользовательских настроек
                "--python",
                script_path,  # Выполнить скрипт
            ]

            if output_path:
                # Можно добавить аргументы для экспорта через скрипт
                cmd.extend(["--", "--output", output_path])

            self.logger.info(f"Запуск Blender: {' '.join(cmd)}")

            # Запускаем с захватом вывода
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # Таймаут 2 минуты
                check=True,  # Бросить исключение при ненулевом коде возврата
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": output_path,
            }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Blender вернул ошибку: {e.returncode}")
            return {
                "success": False,
                "error": f"Blender failed with code {e.returncode}",
                "stdout": e.stdout,
                "stderr": e.stderr,
            }
        except subprocess.TimeoutExpired:
            self.logger.error("Blender превысил таймаут")
            return {"success": False, "error": "Timeout expired"}
        finally:
            # Удаляем временный файл
            os.unlink(script_path)
