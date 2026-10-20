/* =========================
   CARRINHO
========================= */

let carrinho =
    JSON.parse(
        localStorage.getItem(
            "carrinhoAquarismo"
        )
    ) || [];

let total = 0;

/* =========================
   FORMATAÇÃO MONETÁRIA
========================= */

function formatarMoeda(valor) {

    return new Intl.NumberFormat(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    ).format(valor);

}

/* =========================
   LOCAL STORAGE
========================= */

function salvarCarrinho() {

    localStorage.setItem(
        "carrinhoAquarismo",
        JSON.stringify(carrinho)
    );

}

/* =========================
   ADICIONAR PRODUTO
========================= */

function adicionarCarrinho(nome, preco) {

    const produtoExistente =
        carrinho.find(
            item => item.nome === nome
        );

    if (produtoExistente) {

        produtoExistente.quantidade++;

    } else {

        carrinho.push({
            nome,
            preco,
            quantidade: 1
        });

    }

    salvarCarrinho();

    renderizarCarrinho();

}

/* =========================
   RENDERIZAR CARRINHO
========================= */

function renderizarCarrinho() {

    const lista =
        document.getElementById(
            "lista-carrinho"
        );

    if (!lista) return;

    lista.innerHTML = "";

    total = 0;

    let quantidadeTotal = 0;

    if (carrinho.length === 0) {

        lista.innerHTML = `
            <li class="carrinho-vazio">
                Seu carrinho está vazio.
            </li>
        `;

    }

    carrinho.forEach((item, index) => {

        quantidadeTotal += item.quantidade;

        total +=
            item.preco *
            item.quantidade;

        const li =
            document.createElement(
                "li"
            );

        li.innerHTML = `

            <div class="item-carrinho">

                <div>

                    <strong>
                        ${item.nome}
                    </strong>

                    <br>

                    Quantidade:
                    ${item.quantidade}

                    <br>

                    ${formatarMoeda(item.preco)}

                </div>

                <div class="acoes-item">

                    <button
                        class="btn-menos"
                        onclick="diminuirQuantidade(${index})">

                        ➖

                    </button>

                    <button
                        class="btn-mais"
                        onclick="aumentarQuantidade(${index})">

                        ➕

                    </button>

                    <button
                        class="btn-remover"
                        onclick="removerItem(${index})">

                        🗑️

                    </button>

                </div>

            </div>

        `;

        lista.appendChild(li);

    });

    document.getElementById(
        "contador-carrinho"
    ).textContent =
        quantidadeTotal;

    document.getElementById(
        "total"
    ).textContent =
        formatarMoeda(total);

}

/* =========================
   AUMENTAR QUANTIDADE
========================= */

function aumentarQuantidade(index) {

    carrinho[index].quantidade++;

    salvarCarrinho();

    renderizarCarrinho();

}

/* =========================
   DIMINUIR QUANTIDADE
========================= */

function diminuirQuantidade(index) {

    if (
        carrinho[index]
            .quantidade > 1
    ) {

        carrinho[index]
            .quantidade--;

    } else {

        carrinho.splice(
            index,
            1
        );

    }

    salvarCarrinho();

    renderizarCarrinho();

}

/* =========================
   REMOVER ITEM
========================= */

function removerItem(index) {

    carrinho.splice(
        index,
        1
    );

    salvarCarrinho();

    renderizarCarrinho();

}

/* =========================
   ESVAZIAR CARRINHO
========================= */

function esvaziarCarrinho() {

    if (
        !confirm(
            "Deseja esvaziar o carrinho?"
        )
    ) {
        return;
    }

    carrinho = [];

    salvarCarrinho();

    renderizarCarrinho();

}

/* =========================
   ABRIR / FECHAR
========================= */

function abrirCarrinho() {

    document.getElementById(
        "carrinho"
    ).style.display =
        "block";

}

function fecharCarrinho() {

    document.getElementById(
        "carrinho"
    ).style.display =
        "none";

}

/* =========================
   FINALIZAR COMPRA
========================= */

function finalizarCompra() {

    if (
        carrinho.length === 0
    ) {

        alert(
            "Seu carrinho está vazio."
        );

        return;

    }

    let mensagem =
        "Olá, gostaria de comprar:\n\n";

    carrinho.forEach(item => {

        mensagem +=
            `${item.nome} x${item.quantidade} - ${formatarMoeda(
                item.preco *
                item.quantidade
            )}\n`;

    });

    mensagem +=
        `\n💰 Total: ${formatarMoeda(total)}`;

    window.open(
        "https://wa.me/5585999999999?text=" +
        encodeURIComponent(mensagem),
        "_blank"
    );

}

/* =========================
   FILTROS
========================= */

function filtrarProdutos() {

    const busca =
        document
        .getElementById(
            "buscarPeixe"
        )
        .value
        .toLowerCase();

    const categoria =
        document
        .getElementById(
            "filtroCategoria"
        )
        .value;

    const cards =
        document.querySelectorAll(
            ".peixe-card"
        );

}

