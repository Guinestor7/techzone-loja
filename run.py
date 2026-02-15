import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

# Inicializar banco de dados automaticamente
with app.app_context():
    db.create_all()
    # Criar admin e categorias se não existirem
    from app.models import User, Categoria
    if not User.query.first():
        admin = User(
            email='admin@techzone.com',
            nome='Administrador',
            is_admin=True
        )
        admin.set_senha('admin123')
        db.session.add(admin)

        # Criar categorias
        categorias = [
            ('Carregadores', 'carregadores'),
            ('Fones de Ouvido', 'fones-de-ouvido'),
            ('Cabos', 'cabos'),
            ('Capas', 'capas'),
            ('Baterias', 'baterias'),
            ('Outros', 'outros'),
        ]
        for nome, slug in categorias:
            if not Categoria.query.filter_by(slug=slug).first():
                cat = Categoria(nome=nome, slug=slug)
                db.session.add(cat)

        db.session.commit()
        print("✅ Admin e categorias criados automaticamente!")


@app.shell_context_processor
def make_shell_context():
    """Disponibiliza models no shell Flask"""
    return {'db': db, 'app': app}


@app.cli.command()
def init_data():
    """Cria dados iniciais para desenvolvimento"""
    from app.models import User, Categoria

    print("Criando dados iniciais...")

    # Criar usuário admin
    admin = User.query.filter_by(email='admin@loja.com').first()
    if not admin:
        admin = User(
            email='admin@loja.com',
            nome='Administrador',
            is_admin=True
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        print("✓ Usuário admin criado (admin@loja.com / admin123)")

    # Criar categorias
    categorias = [
        ('Carregadores', 'carregadores'),
        ('Fones de Ouvido', 'fones-de-ouvido'),
        ('Cabos', 'cabos'),
        ('Capas', 'capas'),
        ('Baterias', 'baterias'),
        ('Outros', 'outros'),
    ]

    for nome, slug in categorias:
        if not Categoria.query.filter_by(slug=slug).first():
            cat = Categoria(nome=nome, slug=slug)
            db.session.add(cat)
            print(f"✓ Categoria '{nome}' criada")

    db.session.commit()
    print("\nDados iniciais criados com sucesso!")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
