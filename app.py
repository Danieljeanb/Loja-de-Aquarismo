import os
import urllib.parse
from io import BytesIO
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired # For reset token

base_dir = os.path.abspath(os.path.dirname(__file__))
templates_dir = os.path.join(base_dir, 'templates')

# --- LOG DE VERIFICAÇÃO FORÇADA NO TERMINAL ---
print("\n" + "="*50)
print("🔍 MONITORAMENTO DE ARQUIVOS REAL:")
print(f"1. O app.py está na pasta: {base_dir}")
print(f"2. Procurando a pasta templates em: {templates_dir}")

if os.path.exists(templates_dir):
    print("3. ✅ Pasta 'templates' ENCONTRADA!")
    print("4. Arquivos físicos dentro dela:", os.listdir(templates_dir))
else:
    print("3. ❌ Pasta 'templates' NÃO EXISTE nesse caminho!")
    # Tenta procurar pastas parecidas para deduzir o erro
    print("4. Outros arquivos/pastas na raiz:", os.listdir(base_dir))
print("="*50 + "\n")

app = Flask(__name__, 
            template_folder=templates_dir,
            static_folder=os.path.join(base_dir, 'static'))

# Geração de PDF profissional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
# Certifique-se de alterar para uma chave secreta forte em produção
app.secret_key = 'chave_secreta_super_segura_para_sessoes_e_autenticacao'

# Configurações de Upload e Diretórios
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Credenciais de Conexão MySQL (Padrão Corporativo)
USUARIO = 'root'
SENHA = ''          
SERVIDOR = 'localhost'
PORTA = '3306'      
NOME_BANCO = 'aquarismo_pro'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{SENHA}@{SERVIDOR}:{PORTA}/{NOME_BANCO}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Serializador para tokens de redefinição de credenciais
s = URLSafeTimedSerializer(app.secret_key)

# ==========================================
# MODELOS DO BANCO DE DADOS (MySQL)
# ==========================================
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client', nullable=False) # 'client' ou 'employee'
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False) # 'aquario', 'equipamento', 'peixe'
    subcategoria = db.Column(db.String(50), default='geral') # ✨ Nova: 'doce', 'fria', 'premium', etc.
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(255), default='placeholder.jpg')
    estoque = db.Column(db.Integer, default=0, nullable=False) 

class Dica(db.Model):
    __tablename__ = 'dicas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    subtitulo = db.Column(db.String(150), nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    icone = db.Column(db.String(50), default='fa-lightbulb')

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade="all, delete-orphan")

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)


# ==========================================
# ✨ DECORATOR DE PROTEÇÃO DE ACESSO (MIDDLEWARE)
# ==========================================
# def login_required(role_permitido=None):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'user_id' not in session:
#                 flash('Acesso negado. Por favor, realize o login primeiro.', 'danger')
#                 return redirect(url_for('login'))
#             if role_permitido and session.get('user_role') != role_permitido:
#                 flash('Você não possui nível de acesso suficiente para visualizar esta página.', 'danger')
#                 return redirect(url_for('index'))
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ==========================================
# ROTAS DE NAVEGAÇÃO PÚBLICA & DINÂMICA
# ==========================================
@app.route('/')
def index():
    # 🌟 CORREÇÃO: Altere de 'base.html' para 'index.html'
    return render_template('index.html')


@app.route('/base')
def base():
    return render_template('base.html')
@app.route('/aquarios')
def aquarios():
    lista = Produto.query.filter_by(categoria='aquario').all()
    return render_template('aquarios.html', aquarios=lista)

@app.route('/equipamentos')
def equipamentos():
    # Filtra no MySQL apenas os produtos cadastrados com a categoria 'equipamento'
    lista_equipamentos = Produto.query.filter_by(categoria='equipamento').all()
    return render_template('equipamentos.html', equipamentos=lista_equipamentos)


@app.route('/peixes')
def peixes():
    # Suporta filtro por subcategoria vindo via URL parameter (ex: /peixes?sub=premium)
    sub = request.args.get('sub')
    if sub:
        lista = Produto.query.filter_by(categoria='peixe', subcategoria=sub).all()
    else:
        lista = Produto.query.filter_by(categoria='peixe').all()
    return render_template('peixes.html', peixes=lista)

@app.route('/dicas')
def dicas():
    lista = Dica.query.all()
    return render_template('dicas.html', dicas=lista)

# ==========================================
# CONTROLE DE CONTAS E SESSÃO
# ==========================================
@app.route('/perfil')
def perfil():
    usuario = Usuario.query.get(session['user_id'])
    historico_pedidos = Pedido.query.filter_by(user_id=usuario.id).order_by(Pedido.data_pedido.desc()).all()
    return render_template('perfil.html', usuario=usuario, pedidos=historico_pedidos)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome'); email = request.form.get('email'); senha = request.form.get('senha')
        if Usuario.query.filter_by(email=email).first():
            flash('Este endereço de e-mail já está em uso.', 'danger')
            return redirect(url_for('cadastro_cliente'))
        
        hash_seguro = generate_password_hash(senha, method='scrypt')
        db.session.add(Usuario(nome=nome, email=email, senha_hash=hash_seguro, role='client'))
        db.session.commit()
        flash('Cadastro concluído com sucesso! Prossiga com o Login.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')


@app.route('/carrinho')
def visualizar_carrinho():  # ✅ Nome correto que a navbar flutuante está chamando
    carrinho = session.get('carrinho', {})
    itens_carrinho = []
    total = 0.0
    
    for id_str, qtd in carrinho.items():
        produto = db.session.get(Produto, int(id_str))
        if produto:
            subtotal = produto.preco * qtd
            total += subtotal
            itens_carrinho.append({
                'produto': produto,
                'quantidade': qtd,
                'subtotal': subtotal
            })
            
    session.modified = True
    return render_template('carrinho.html', itens=itens_carrinho, total=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email'); senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nome
            session['user_role'] = usuario.role
            flash(f'Olá {usuario.nome}, login efetuado com sucesso!', 'success')
            return redirect(url_for('admin') if usuario.role == 'employee' else url_for('index'))
        flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('index'))

# ==========================================
# SISTEMA DE RECUPERAÇÃO DE ACESSO
# ==========================================
@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            token = s.dumps(email, salt='recuperacao-senha-salt')
            link_recuperacao = url_for('redefinir_senha', token=token, _external=True)
            # Log de Simulação no Console
            print(f"\n[SERVER CONTROLE]: Link gerado para {email} -> {link_recuperacao}\n")
            flash('Instruções de redefinição enviadas! Verifique o console de execução do servidor.', 'success')
            return redirect(url_for('login'))
        flash('Nenhum usuário localizado com este e-mail.', 'danger')
    return render_template('recuperar_senha.html')

@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    try:
        email = s.loads(
            token,
            salt='recuperacao-senha-salt',
            max_age=1800
        )
    except SignatureExpired:
        flash('O prazo do token de segurança expirou (Limite: 30 min).', 'danger')
        return redirect(url_for('recuperar_senha'))
    except Exception:
        flash('Token inválido ou corrompido.', 'danger')
        return redirect(url_for('recuperar_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario.senha_hash = generate_password_hash(
                nova_senha,
                method='scrypt'
            )

            db.session.commit()

            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('login'))

    return render_template(
        'redefinir_senha.html',
        token=token
    )

def visualizar_carrinho():
    carrinho = session.get('carrinho', {})
    itens_carrinho = []
    total = 0.0

    for id_str, qtd in carrinho.items():
        # ✨ CORREÇÃO: Utiliza o método moderno db.session.get para evitar erros no SQLAlchemy 3.0+
        produto = db.session.get(Produto, int(id_str))
        
        if produto:
            subtotal = produto.preco * qtd
            total += subtotal
            itens_carrinho.append({
                'produto': produto,
                'quantidade': qtd,
                'subtotal': subtotal
            })

    # ✨ MELHORIA: Garante que o Flask salve a sessão caso alguma modificação ocorra em segundo plano
    session.modified = True
    
    return render_template('carrinho.html', itens=itens_carrinho, total=total)



@app.route('/adicionar_carrinho/<int:produto_id>', methods=['POST'])
def adicionar_carrinho(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    if 'carrinho' not in session:
        session['carrinho'] = {}

    carrinho = session['carrinho']
    id_str = str(produto_id)
    if carrinho.get(id_str, 0) >= produto.estoque:
        flash(f'Lote esgotado! Não temos mais unidades de "{produto.nome}" em estoque.', 'danger')
        return redirect(request.referrer or url_for('index'))

    carrinho[id_str] = carrinho.get(id_str, 0) + 1
    session['carrinho'] = carrinho
    flash(f'"{produto.nome}" adicionado com sucesso!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/limpar_carrinho')
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect(url_for('visualizar_carrinho'))


@app.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    carrinho = session.get('carrinho', {})
    if not carrinho:
        flash('Impossível finalizar um carrinho vazio.', 'danger')
        return redirect(url_for('visualizar_carrinho'))

    total_geral = 0.0
    lista_itens_db = []
    texto_whatsapp = "📥 NOVO PEDIDO CONFIRMADO - AQUARISMO PRO\n\n"
    if 'user_id' in session:
        texto_whatsapp += f"👤 Comprador: {session['user_name']}\n\n"

    # Validação e Processamento de Baixa de Inventário
    for id_str, qtd in carrinho.items():
        produto = Produto.query.get(int(id_str))
        if not produto or produto.estoque < qtd:
            flash(f'Estoque quebrou! O item {produto.nome if produto else "solicitado"} esgotou.', 'danger')
            return redirect(url_for('visualizar_carrinho'))

        subtotal = produto.preco * qtd
        total_geral += subtotal
        produto.estoque -= qtd
        lista_itens_db.append(ItemPedido(
            produto_nome=produto.nome,
            quantidade=qtd,
            preco_unitario=produto.preco,
        ))
        texto_whatsapp += f"• {qtd}x {produto.nome} - R$ {subtotal:.2f}\n"

    texto_whatsapp += f"\n💰 VALOR TOTAL DO PEDIDO: R$ {total_geral:.2f}"
    novo_pedido = Pedido(total=total_geral, itens=lista_itens_db, user_id=session.get('user_id'))
    db.session.add(novo_pedido)
    db.session.commit()

    TELEFONE_CONTATO = "5585999999999"
    link_final_whatsapp = f"https://wa.me/{TELEFONE_CONTATO}?text={urllib.parse.quote(texto_whatsapp)}"
    session.pop('carrinho', None)
    return render_template('sucesso.html', link_whatsapp=link_final_whatsapp, pedido_id=novo_pedido.id)


# GERAÇÃO CONTÁBIL E DOCUMENTAL (PDF)


@app.route('/gerar_pdf/<int:pedido_id>')
def gerar_pdf(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Customização Estilizada do PDF
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor('#0070f3'),
        spaceAfter=15,
    )
    elements.append(Paragraph("Recibo de Compra - Aquarismo Pro", title_style))
    elements.append(Paragraph(f"Código do Pedido: #000{pedido.id}", styles['Normal']))
    elements.append(Paragraph(
        f"Data da Operação: {pedido.data_pedido.strftime('%d/%m/%Y %H:%M:%S')}",
        styles['Normal'],
    ))
    if pedido.cliente:
        elements.append(Paragraph(
            f"Cliente: {pedido.cliente.nome} ({pedido.cliente.email})",
            styles['Normal'],
        ))
    else:
        elements.append(Paragraph("Cliente: Balcão / Anônimo", styles['Normal']))

    elements.append(Spacer(1, 15))

    # Grid de Itens
    data = [['Produto / Espécie', 'Quantidade', 'Preço Unitário', 'Subtotal']]
    for item in pedido.itens:
        sub = item.quantidade * item.preco_unitario
        data.append([
            item.produto_nome,
            str(item.quantidade),
            f"R$ {item.preco_unitario:.2f}",
            f"R$ {sub:.2f}",
        ])

    table = Table(data, colWidths=[240, 70, 100, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Valor Total Pago: R$ {pedido.total:.2f}", styles['Heading2']))
    doc.build(elements)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"recibo_pedido_{pedido.id}.pdf",
        mimetype='application/pdf',
    )


# PAINEL ADMINISTRATIVO (RESTRITO)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'produto':
            nome = request.form.get('nome')
            categoria = request.form.get('categoria')
            subcategoria = request.form.get('subcategoria', 'geral')
            descricao = request.form.get('descricao')
            preco = float(request.form.get('preco'))
            estoque = int(request.form.get('estoque'))
            file = request.files.get('imagem')
            nome_arquivo = 'placeholder.jpg'
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                nome_arquivo = filename

            novo_prod = Produto(
                nome=nome,
                categoria=categoria,
                subcategoria=subcategoria,
                descricao=descricao,
                preco=preco,
                imagem=nome_arquivo,
                estoque=estoque,
            )
            db.session.add(novo_prod)
            db.session.commit()
            flash('Produto catalogado com sucesso!', 'success')
            return redirect(url_for('admin'))

    return render_template('admin.html', produtos=Produto.query.all(), dicas=Dica.query.all())

# Cole isso temporariamente para diagnosticar:
print("--- DIAGNÓSTICO DE PASTAS DO FLASK ---")
print("O Python está rodando dentro de:", os.getcwd())
print("A pasta templates existe aqui?", os.path.exists('templates'))
if os.path.exists('templates'):
    print("Arquivos encontrados dentro de templates:", os.listdir('templates'))
print("---------------------------------------")


# SCRIPT STARTUP CONTEXT

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    with app.app_context():
        db.create_all()
    app.run(debug=True)