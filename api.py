from flask import Flask, jsonify, request
from PIL import Image, ImageDraw, ImageFont
import boto3
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def webhook_typebot():
    # Verificar se 'nome' e 'cpf' foram enviados como parâmetros de consulta
    if 'nome' not in request.args or 'cpf' not in request.args:
        return "Erro: Nenhum nome e/ou cpf fornecido.", 400

    nome = request.args['nome']  # Acessando o nome enviado via parâmetro de consulta
    cpf = request.args['cpf']  # Acessando o cpf enviado via parâmetro de consulta

    # Suas operações de manipulação de imagem
    cord_nome1 = (585, 410)
    cord_nome2 = (1142, 212)
    cord_cpf = (1350, 212)

    doc = "CPF " + cpf

    # Baixar a imagem da internet
    url_imagem = 'https://rendaoficial.online/wp-content/uploads/2024/02/certificadop.jpg'
    response = requests.get(url_imagem)
    imagem = Image.open(BytesIO(response.content))

    # Usar uma fonte padrão do sistema (Sans-serif)
    font = ImageFont.load_default()

    rgb_preto = (0,0,0)
    desenho = ImageDraw.Draw(imagem)
    desenho.text(cord_nome1, nome, font=font, fill=rgb_preto)
    desenho.text(cord_nome2, nome, font=font, fill=rgb_preto)
    desenho.text(cord_cpf, doc, font=font, fill=rgb_preto)

    # Configuração do cliente S3
    s3_client = boto3.client('s3')
    bucket_name = 'hosprusk'
    s3_file_name = f'certificados/{nome}-{cpf}.jpg'

    # Salvar imagem em um buffer
    img_buffer = BytesIO()
    imagem.save(img_buffer, format='JPEG')
    img_buffer.seek(0)

    # Upload da imagem para o S3
    s3_client.upload_fileobj(
        img_buffer,
        bucket_name,
        s3_file_name,
        ExtraArgs={
            'ContentType': 'image/jpeg',
        }
    )

    # Gerar o URL público
    url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"

    # Retornar o URL como resposta
    return jsonify({'url': url})

if __name__ == '__main__':
    app.run(debug=True)
