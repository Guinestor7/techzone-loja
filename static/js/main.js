// TechZone - JavaScript principal

document.addEventListener('DOMContentLoaded', function() {
    // Atualiza contador do carrinho
    updateCartCount();

    // Inicializa tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

function updateCartCount() {
    fetch('/api/carrinho/count')
        .then(response => response.json())
        .then(data => {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.count;
                cartCount.style.display = data.count > 0 ? 'inline' : 'none';
            }
        })
        .catch(error => console.error('Erro ao atualizar carrinho:', error));
}

// Função para adicionar ao carrinho
function addToCart(productId, quantity = 1) {
    fetch(`/carrinho/adicionar/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            // Mostra toast ou alerta
            alert('Produto adicionado ao carrinho!');
        } else {
            alert(data.message || 'Erro ao adicionar produto');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao adicionar produto ao carrinho');
    });
}

// Função para copiar código Pix
function copyPixCode() {
    const pixCode = document.getElementById('pix-copy-paste');
    if (pixCode) {
        navigator.clipboard.writeText(pixCode.textContent).then(() => {
            alert('Código Pix copiado!');
        });
    }
}
