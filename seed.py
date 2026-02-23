import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from imoveis.models import Produto

def popular_loja():
    categorias = ["Móveis", "Eletrodomésticos", "Informática", "Smartphones", "Lazer"]
    
    produtos_por_categoria = {
        "Móveis": ["Cadeira Gamer", "Sofá 3 Lugares", "Mesa de Jantar", "Guarda-Roupa"],
        "Eletrodomésticos": ["Geladeira Frost Free", "Máquina de Lavar", "Micro-ondas"],
        "Informática": ["Notebook i7", "Monitor 24p", "Teclado Mecânico", "Mouse Sem Fio"],
        "Smartphones": ["iPhone 15", "Galaxy S24", "Redmi Note 13"],
        "Lazer": ["Bicicleta Aro 29", "Piscina 3000L", "Churrasqueira Elétrica"]
    }

    print("Preparando 1000 produtos de varejo...")
    lista_para_inserir = []

    for i in range(1, 1001):
        cat = random.choice(categorias)
        nome_prod = random.choice(produtos_por_categoria[cat])
        
        novo_item = Produto(
            tipo=cat, 
            produto=f"{nome_prod} Mod. {random.randint(100, 999)}",
            preco=random.uniform(50.0, 5000.0),
            qtd_vendas=random.randint(0, 100),
            faturamento=random.uniform(50.0, 5000.0) * random.randint(0, 100),
            mes=random.randint(1, 12),
            ano=2026,
            sku=f"CB-{random.randint(10000, 99999)}-{i}" 
        )
        lista_para_inserir.append(novo_item)

    Produto.objects.bulk_create(lista_para_inserir)
    print(f"Sucesso! 1000 produtos da loja inseridos no MySQL.")

if __name__ == "__main__":
    popular_loja()