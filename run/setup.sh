set -e  # Exit on any error

echo "🚀 Setting up aiogram-mock development environment on Ubuntu..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install Python 3.8+ if not present
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo apt install -y python3 python3-pip python3-venv
else
    echo "Python3 is already installed: $(python3 --version)"
fi

# Install uv (modern Python package manager)
echo "📥 Installing uv package manager..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
else
    echo "uv is already installed: $(uv --version)"
fi

# Create virtual environment
echo "🏠 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Install package in development mode
echo "🔧 Installing aiogram-mock in development mode..."
uv pip install -e .

# Install development dependencies
echo "🛠️  Installing development dependencies..."
uv pip install -r requirements.txt