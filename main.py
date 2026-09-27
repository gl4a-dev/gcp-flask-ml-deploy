from flask import Flask, jsonify

app = Flask(__name__)

HTML_GUIDE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guia de Deploy & CI/CD - App Engine</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #202124; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
        h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px; }
        h2 { color: #202124; margin-top: 24px; }
        pre { background: #282c34; color: #abb2bf; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: "Fira Code", Monaco, monospace; font-size: 0.9em; }
        code { background: #e8eaed; color: #202124; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        ul, ol { padding-left: 20px; }
        li { margin-bottom: 8px; }
    </style>
</head>
<body>
    <h1>Guia de Deploy no App Engine (Standard) & CI/CD com Cloud Build</h1>

    <div class="card">
        <h2>1. Estrutura de Arquivos do Repositório</h2>
        <p>A raiz do projeto deve conter a seguinte estrutura:</p>
        <pre>├── main.py              # Aplicação Flask
├── app.yaml             # Configuração do App Engine
├── requirements.txt     # Dependências Python
├── .gcloudignore        # Arquivos ignorados no upload
└── cloudbuild.yaml      # Pipeline de CI/CD</pre>
        
        <h3>Configurações dos Arquivos:</h3>
        <p><strong>app.yaml</strong></p>
        <pre>runtime: python312
entrypoint: gunicorn -b :$PORT main:app
automatic_scaling:
  max_instances: 2</pre>

        <p><strong>requirements.txt</strong></p>
        <pre>flask
gunicorn</pre>

        <p><strong>.gcloudignore</strong></p>
        <pre>.git
.gitignore
venv/
.venv/
env/
__pycache__/
*.pyc
cloudbuild.yaml</pre>

        <p><strong>cloudbuild.yaml</strong></p>
        <pre>steps:
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: ['app', 'deploy', '--project=$PROJECT_ID', '-q']
options:
  logging: CLOUD_LOGGING_ONLY
timeout: '1800s'</pre>
    </div>

    <div class="card">
        <h2>2. Configuração Inicial e APIs no GCP</h2>
        <p>Execute no Cloud Shell:</p>
        <pre># Definir projeto ativo e ativar serviços
gcloud config set project SEU_PROJECT_ID

gcloud services enable \
  appengine.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  containerregistry.googleapis.com

# Criar a aplicação App Engine
gcloud app create --region=southamerica-east1</pre>
    </div>

    <div class="card">
        <h2>3. Atribuição de Permissões (IAM)</h2>
        <pre>PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Permissões do Cloud Build
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/appengine.appAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Permissões da Compute Engine Service Account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/appengine.deployer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

# Autorização de Impersonation
gcloud iam service-accounts add-iam-policy-binding \
  ${PROJECT_ID}@appspot.gserviceaccount.com \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"</pre>
    </div>

    <div class="card">
        <h2>4. Deploy Manual Inicial & Gatilho GitHub</h2>
        <ol>
            <li>Faça o primeiro deploy manual no terminal: <code>gcloud app deploy</code></li>
            <li>Acesse <strong>Cloud Build</strong> &gt; <strong>Gatilhos</strong> &gt; <strong>Criar gatilho</strong></li>
            <li>Conecte o repositório via <strong>Developer Connect</strong> no evento de push na branch <code>^main$</code></li>
            <li>Configure o local do arquivo como <code>cloudbuild.yaml</code> e marque os registros como <strong>Apenas Cloud Logging</strong></li>
        </ol>
    </div>
</body>
</html>
"""

@app.route('/')
def hello():
    """Retorna o guia visual de deploy e CI/CD em formato HTML."""
    return HTML_GUIDE

@app.route('/echo/<name>')
def echo(name):
    """Exemplo de rota utilitária em JSON."""
    return jsonify({"new-name": name})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
