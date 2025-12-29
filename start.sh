if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python n'est pas installé"
    echo "Veuillez installer Python depuis https://www.python.org/"
    exit 1
fi



if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[INFO] Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERREUR] Échec de l'installation des dépendances"
        exit 1
    fi
    echo "[OK] Dépendances installées"
    echo ""
fi

streamlit run simulateur_immobilier.py
