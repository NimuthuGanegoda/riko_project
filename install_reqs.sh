### CHECK NVIDIA VERSION WITH NVIDIA-SMI I HAVE 12.7 BUT IF YOU HAVE 12.8 UV pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu12

pip install uv
pip install torch==2.6.0 torchaudio --index-url https://download.pytorch.org/whl/cu126
uv pip install -r extra-req.txt --no-deps
uv pip install -r requirements.txt
uv pip install google-auth google-auth-oauthlib

echo "--------------------------------------------------------"
echo "🌟 TRIGGERING GOOGLE PRO AUTHENTICATION 🌟"
echo "Senpai, I'm opening your browser so you can sign in!"
echo "This will let me use your Google Pro subscription."
echo "--------------------------------------------------------"
gcloud auth application-default login || echo "Note: gcloud CLI not found. Please install it to use browser-based login, or use an API key."

python - <<PYCODE
import nltk
for pkg in ["averaged_perceptron_tagger", "cmudict"]:
    nltk.download(pkg)
PYCODE
