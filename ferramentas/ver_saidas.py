r"""Executa um caderno de resolvidos/ e mostra as saídas de texto de cada célula (para conferir os números).

Uso (na raiz):  .venv\Scripts\python.exe ferramentas\ver_saidas.py 11
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import nbformat
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parent.parent
cap = int(sys.argv[1])
nb_path = next((RAIZ / "resolvidos").glob(f"cap{cap:02d}_*.ipynb"))
nb = nbformat.read(nb_path, as_version=4)
NotebookClient(nb, timeout=900, kernel_name="python3", allow_errors=True,
               resources={"metadata": {"path": str(nb_path.parent)}}).execute()
for c in nb.cells:
    if c.cell_type != "code":
        continue
    txt = []
    for o in c.outputs:
        if o.output_type == "stream":
            txt.append(o.text)
        elif o.output_type in ("execute_result", "display_data") and "text/plain" in o.get("data", {}):
            txt.append(o["data"]["text/plain"][:1500])
        elif o.output_type == "error":
            txt.append("ERRO: " + o.ename + ": " + o.evalue)
    if txt:
        print("-----", c.source.splitlines()[0][:70])
        print("".join(txt)[:2500])
