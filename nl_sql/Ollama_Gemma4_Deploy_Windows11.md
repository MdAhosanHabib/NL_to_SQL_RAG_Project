Ollama Download for Windows exe file:
https://ollama.com/download/windows

## go to powershell
cd 'E:\Software\programming tools\AI_ML\'
.\OllamaSetup.exe /DIR="E:\Ollama\Ollama_APP"

Create a folder on your D: drive specifically for the models. For My: E:\Ollama\Ollama_Model.

Then go to Ollama setting UI and set Model Location.

## go to powershell
ollama run gemma4:26b

ollama pull nomic-embed-text
ollama list   # confirm both models appear

[root@de aidb]# curl http://192.168.0.102:11434/api/tags

