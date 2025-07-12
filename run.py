import sys
from os.path import abspath, dirname

# Add project root to Python path
sys.path.insert(0, dirname(abspath(__file__)))  # C:\Projects\SkillSwap

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
