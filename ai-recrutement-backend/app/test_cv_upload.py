"""
Interface web pour tester l'extraction de CV avec sauvegarde.
Lance avec: python test_cv_upload.py
Puis visite: http://localhost:8000
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.analyse_cv import analyser_cv_pdf

app = FastAPI(title="Test Extraction CV - LangChain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def interface_test():
    """Interface d'upload de CV PDF"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload CV PDF - LangChain + DB</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }
            
            .container {
                max-width: 1100px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #666;
                font-size: 1.1em;
            }
            
            .badge {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-size: 0.9em;
                margin-bottom: 20px;
                font-weight: 600;
            }
            
            .tech-badge {
                display: inline-block;
                background: #48bb78;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 0.85em;
                margin: 0 5px;
            }
            
            .upload-zone {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 60px 40px;
                text-align: center;
                background: #f8f9ff;
                transition: all 0.3s;
                cursor: pointer;
                margin-bottom: 30px;
            }
            
            .upload-zone:hover {
                background: #eef1ff;
                border-color: #764ba2;
            }
            
            .upload-zone.dragover {
                background: #e0e7ff;
                border-color: #5a67d8;
            }
            
            .upload-icon {
                font-size: 4em;
                margin-bottom: 20px;
            }
            
            input[type="file"] {
                display: none;
            }
            
            .file-info {
                margin: 20px 0;
                padding: 15px;
                background: #e0e7ff;
                border-radius: 10px;
                display: none;
            }
            
            .file-info.show {
                display: block;
            }
            
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 18px 50px;
                border-radius: 12px;
                font-size: 1.2em;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            
            button:hover:not(:disabled) {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
            }
            
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin: 30px 0;
            }
            
            .loading.show {
                display: block;
            }
            
            .spinner {
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-steps {
                color: #667eea;
                font-weight: 600;
                margin-top: 15px;
            }
            
            .loading-steps div {
                margin: 5px 0;
                padding: 8px;
                background: #f0f0f0;
                border-radius: 5px;
            }
            
            .loading-steps .active {
                background: #e0e7ff;
                color: #667eea;
            }
            
            .resultat {
                margin-top: 40px;
                padding: 30px;
                background: #f8f9fa;
                border-radius: 15px;
                border-left: 5px solid #667eea;
                display: none;
            }
            
            .resultat.show {
                display: block;
                animation: slideIn 0.5s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .resultat h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            
            .cv-info {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .cv-info h3 {
                color: #764ba2;
                margin-bottom: 10px;
                font-size: 1.2em;
            }
            
            .cv-info p {
                color: #555;
                margin: 5px 0;
                line-height: 1.6;
            }
            
            .tag {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 5px 12px;
                border-radius: 15px;
                margin: 5px 5px 5px 0;
                font-size: 0.85em;
            }
            
            .success-box {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            
            .success-box h3 {
                color: #155724;
                margin-bottom: 10px;
            }
            
            .success-box p {
                color: #155724;
                margin: 5px 0;
            }
            
            .json-toggle {
                background: #2d3748;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 15px;
                font-size: 0.95em;
            }
            
            pre {
                background: #2d3748;
                color: #68d391;
                padding: 25px;
                border-radius: 10px;
                overflow-x: auto;
                font-size: 0.9em;
                line-height: 1.7;
                display: none;
                margin-top: 15px;
            }
            
            pre.show {
                display: block;
            }
            
            .error {
                background: #fee;
                border-left-color: #f44;
            }
            
            .error h2 {
                color: #c33;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="badge">🎯 Membre 3 - Niveau 2 - Production</div>
                <h1>📄 Analyse CV avec Sauvegarde</h1>
                <p class="subtitle">Upload PDF → Extraction IA → Sauvegarde locale + JSON en base</p>
                <div style="margin-top: 15px;">
                    <span class="tech-badge">🦜 LangChain</span>
                    <span class="tech-badge">⚡ Groq</span>
                    <span class="tech-badge">💾 PDF Storage</span>
                    <span class="tech-badge">🗄️ PostgreSQL</span>
                </div>
            </div>
            
            <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📤</div>
                <h3 style="color: #667eea; margin-bottom: 10px;">Cliquez ou glissez-déposez un CV PDF</h3>
                <p style="color: #888;">Format accepté: PDF • Taille max: 10 MB</p>
                <input type="file" id="fileInput" accept=".pdf" onchange="handleFile(this.files[0])">
            </div>
            
            <div class="file-info" id="fileInfo">
                <strong>📎 Fichier sélectionné:</strong>
                <p id="fileName"></p>
                <p id="fileSize"></p>
            </div>
            
            <div style="text-align: center;">
                <button id="analyseBtn" onclick="analyserCV()" disabled>
                    🚀 Analyser et Sauvegarder
                </button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="color: #667eea; font-size: 1.1em; font-weight: 600;">Analyse en cours...</p>
                <div class="loading-steps" id="loadingSteps">
                    <div id="step1">⏳ Extraction du texte PDF...</div>
                    <div id="step2">⏳ Analyse IA avec LangChain...</div>
                    <div id="step3">⏳ Sauvegarde du PDF...</div>
                    <div id="step4">⏳ Génération du JSON...</div>
                </div>
            </div>
            
            <div class="resultat" id="resultat"></div>
        </div>
        
        <script>
            let fichierSelectionne = null;
            let jsonData = null;
            
            const uploadZone = document.getElementById('uploadZone');
            
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });
            
            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('dragover');
            });
            
            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                const file = e.dataTransfer.files[0];
                if (file && file.type === 'application/pdf') {
                    handleFile(file);
                }
            });
            
            function handleFile(file) {
                if (!file) return;
                
                if (file.type !== 'application/pdf') {
                    alert('⚠️ Seuls les fichiers PDF sont acceptés');
                    return;
                }
                
                fichierSelectionne = file;
                
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = `Taille: ${(file.size / 1024).toFixed(2)} KB`;
                document.getElementById('fileInfo').classList.add('show');
                document.getElementById('analyseBtn').disabled = false;
            }
            
            async function analyserCV() {
                if (!fichierSelectionne) return;
                
                const formData = new FormData();
                formData.append('file', fichierSelectionne);
                
                document.getElementById('loading').classList.add('show');
                document.getElementById('resultat').classList.remove('show');
                document.getElementById('analyseBtn').disabled = true;
                
                // Animation des étapes
                setTimeout(() => document.getElementById('step1').classList.add('active'), 500);
                setTimeout(() => document.getElementById('step2').classList.add('active'), 2000);
                setTimeout(() => document.getElementById('step3').classList.add('active'), 4000);
                setTimeout(() => document.getElementById('step4').classList.add('active'), 5000);
                
                try {
                    const response = await fetch('/analyser-pdf', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    jsonData = data;
                    
                    document.getElementById('loading').classList.remove('show');
                    document.getElementById('analyseBtn').disabled = false;
                    
                    // Reset steps
                    ['step1', 'step2', 'step3', 'step4'].forEach(id => {
                        document.getElementById(id).classList.remove('active');
                    });
                    
                    afficherResultat(data);
                    
                } catch (error) {
                    document.getElementById('loading').classList.remove('show');
                    document.getElementById('resultat').innerHTML = `
                        <h2>❌ Erreur</h2>
                        <p>${error.message}</p>
                    `;
                    document.getElementById('resultat').classList.add('show', 'error');
                    document.getElementById('analyseBtn').disabled = false;
                }
            }
            
            function afficherResultat(data) {
                const resultatDiv = document.getElementById('resultat');
                
                if (!data.cv_json || (!data.cv_json.nom && !data.cv_json.email)) {
                    resultatDiv.className = 'resultat error show';
                    resultatDiv.innerHTML = `
                        <h2>⚠️ Extraction incomplète</h2>
                        <p>Vérifiez votre clé API Groq dans le fichier .env</p>
                        <button class="json-toggle" onclick="toggleJSON()">Voir le JSON brut</button>
                        <pre id="jsonData">${JSON.stringify(data, null, 2)}</pre>
                    `;
                    return;
                }
                
                const cv = data.cv_json;
                
                let html = `
                    <h2>✅ CV Analysé et Sauvegardé</h2>
                    
                    <div class="success-box">
                        <h3>💾 Sauvegarde réussie</h3>
                        <p><strong>📁 PDF sauvegardé dans:</strong> ${data.fichier_chemin || 'uploads/cvs/'}</p>
                        <p><strong>📊 JSON extrait:</strong> ${data.texte_length} caractères de texte</p>
                        <p><strong>🗄️ Base de données:</strong> Prêt pour insertion dans la table cvs</p>
                    </div>
                    
                    <div class="cv-info">
                        <h3>👤 Informations Personnelles</h3>
                        <p><strong>Nom:</strong> ${cv.nom || 'Non spécifié'}</p>
                        <p><strong>Email:</strong> ${cv.email || 'Non spécifié'}</p>
                        <p><strong>Téléphone:</strong> ${cv.telephone || 'Non spécifié'}</p>
                    </div>
                `;
                
                if (cv.competences && cv.competences.length > 0) {
                    html += `
                        <div class="cv-info">
                            <h3>💡 Compétences (${cv.competences.length})</h3>
                            <div>
                                ${cv.competences.map(c => `<span class="tag">${c}</span>`).join('')}
                            </div>
                        </div>
                    `;
                }
                
                if (cv.experiences && cv.experiences.length > 0) {
                    html += `<div class="cv-info"><h3>💼 Expériences (${cv.experiences.length})</h3>`;
                    cv.experiences.forEach(exp => {
                        html += `
                            <p><strong>${exp.poste}</strong> - ${exp.entreprise || 'Entreprise non spécifiée'}</p>
                            <p style="color: #888; font-size: 0.9em;">${exp.periode || 'Période non spécifiée'}</p>
                            <p style="margin-top: 5px;">${exp.description || ''}</p>
                            <hr style="margin: 15px 0; border: none; border-top: 1px solid #eee;">
                        `;
                    });
                    html += `</div>`;
                }
                
                if (cv.formations && cv.formations.length > 0) {
                    html += `<div class="cv-info"><h3>🎓 Formations (${cv.formations.length})</h3>`;
                    cv.formations.forEach(form => {
                        html += `
                            <p><strong>${form.diplome}</strong></p>
                            <p style="color: #888;">${form.etablissement || ''} • ${form.annee || ''}</p>
                            <hr style="margin: 15px 0; border: none; border-top: 1px solid #eee;">
                        `;
                    });
                    html += `</div>`;
                }
                
                if (cv.langues && cv.langues.length > 0) {
                    html += `
                        <div class="cv-info">
                            <h3>🌍 Langues</h3>
                            <div>
                                ${cv.langues.map(l => `<span class="tag">${l}</span>`).join('')}
                            </div>
                        </div>
                    `;
                }
                
                html += `
                    <button class="json-toggle" onclick="toggleJSON()">
                        📋 Voir le JSON complet (pour la DB)
                    </button>
                    <pre id="jsonData">${JSON.stringify(data.cv_json, null, 2)}</pre>
                `;
                
                resultatDiv.innerHTML = html;
                resultatDiv.className = 'resultat show';
            }
            
            function toggleJSON() {
                document.getElementById('jsonData').classList.toggle('show');
            }
        </script>
    </body>
    </html>
    """


@app.post("/analyser-pdf")
async def analyser_pdf_endpoint(file: UploadFile = File(...)):
    """Endpoint pour analyser un CV PDF avec sauvegarde"""
    try:
        if not file.filename.endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"error": "Seuls les fichiers PDF sont acceptés"}
            )
        
        contenu_pdf = await file.read()
        
        print(f"📂 Fichier reçu: {file.filename} ({len(contenu_pdf)} octets)")
        
        # Analyser avec LangChain + sauvegarder
        cv_json, texte_brut, chemin_pdf = analyser_cv_pdf(
            contenu_pdf, 
            file.filename,
            sauvegarder_pdf=True
        )
        
        return JSONResponse(content={
            "cv_json": cv_json,
            "texte_brut": texte_brut[:500] + "..." if len(texte_brut) > 500 else texte_brut,
            "texte_length": len(texte_brut),
            "fichier_chemin": chemin_pdf,
            "message": "✅ CV analysé et sauvegardé avec succès"
        })
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 SERVEUR DE TEST CV PDF LANCÉ")
    print("="*70)
    print("📍 Interface web: http://localhost:8000")
    print("🎯 Upload PDF → Analyse IA → Sauvegarde locale + JSON")
    print("💾 Les PDF sont sauvegardés dans: uploads/cvs/")
    print("🗄️ Le JSON est prêt pour la table cvs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)