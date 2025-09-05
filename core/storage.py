from pathlib import Path
import json
from typing import List




def read_jsonl(path: Path) -> List[dict]:
    if not Path(path).exists():
       return []
    with open(path, 'r', encoding='utf-8') as f:
       return [json.loads(line) for line in f if line.strip()]