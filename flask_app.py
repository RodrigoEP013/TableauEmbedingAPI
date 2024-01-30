import datetime
import uuid
import jwt
from flask import Flask, jsonify, render_template
from tableau_api_lib import api_endpoints, api_requests, decorators, exceptions, utils
from tableau_api_lib.sample import sample_config
from tableau_api_lib.tableau_server_connection import TableauServerConnection

userid = "rodrigo.esquerra@egosbi.com"
client_id = "b9ea6bb4-2056-4fa6-aeb4-3ae1f093e0e2"
secret_id = "30ce8619-82f6-4740-b27a-34443848f34b"
secret_value = "l+iXxYFOWr6X5Zliq0FahVbwtoC+KqoqbXRXs6/8aWo="

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_newWorkbook', methods=['GET'])
def get_newWorkbook():
    config = {
        'tableau_prod': {
            'server': 'https://prod-useast-b.online.tableau.com/',
            'api_version': '3.21',
            'personal_access_token_name': 'RESTAPI',
            'personal_access_token_secret': 'N3fae46WR+CkGYA2Lspg2w==:J6RsyQzUEWsHEzsToAasvmwB0LBoRUbn',
            'site_name': 'egosbi',
            'site_url': ''
        }
    }
    
    project_id="e149aec9-dc9b-437a-8385-1c396b40ec08"
    
    conn = TableauServerConnection(config_json=config, env='tableau_prod')
    response=conn.sign_in()
    print(response)
    
    workbook_name = "NewWorkbook"  # Aquí deberías obtener el nombre del libro de trabajo de alguna manera
    response = conn.publish_workbook(
        project_id=project_id,
        workbook_file_path="NewWorkbook.twb",
        workbook_name=workbook_name
    ) 
    
    print(response)
    
    # Verificar que el libro de trabajo se haya publicado correctamente
    if response:
        # Generar el token
        token = jwt.encode(
            {
                "iss": client_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
                "jti": str(uuid.uuid4()),
                "aud": "tableau",
                "sub": userid,
                "scp": ["tableau:views:embed", "tableau:content:read", "tableau:views:embed_authoring"]
            },
            secret_value,
            algorithm="HS256",
            headers={
                'kid': secret_id,
                'iss': client_id
            }
        )

        # Devolver el nombre del libro como parte de la respuesta JSON
        response_data = {
            'workbook_name': workbook_name,
            'token': token
        }
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'No se pudo publicar el libro de trabajo'}), 500

if __name__ == '__main__':
    app.run(debug=True)
