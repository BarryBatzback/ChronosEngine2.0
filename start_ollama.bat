@echo off
set OLLAMA_MODELS=%CD%\models
if not exist %CD%\models mkdir %CD%\models
ollama serve
