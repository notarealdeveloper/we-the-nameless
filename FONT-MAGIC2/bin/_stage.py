import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fontmagic.pipeline import main
def run(command): sys.argv.insert(1,command); main()
