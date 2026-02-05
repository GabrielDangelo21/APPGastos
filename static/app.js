"use strict";

// Seletores de elementos do DOM
const transactionForm = document.getElementById("transaction-form");
const transactionTableBody = document.querySelector("#transaction-table tbody");
const selectConta = document.getElementById("conta");
const selectCategoria = document.getElementById("categoria");

// Elementos de Resumo
const labelReceitas = document.getElementById("total-receitas");
const labelDespesas = document.getElementById("total-despesas");
const labelSaldo = document.getElementById("saldo-atual");

/* ---------- Funções de Busca (Fetch) ---------- */

// 1. Carrega as opções de Contas e Categorias nos selects do formulário principal
async function carregarMetadados() {
    try {
        const [resContas, resCats] = await Promise.all([
            fetch('/api/contas'),
            fetch('/api/categorias')
        ]);

        const contas = await resContas.json();
        const categorias = await resCats.json();

        // Preencher Select de Contas
        selectConta.innerHTML = '<option value="">Selecione a Conta</option>';
        contas.forEach(c => {
            selectConta.innerHTML += `<option value="${c.id}">${c.nome_instituicao} (${c.moeda})</option>`;
        });

        // Preencher Select de Categorias
        selectCategoria.innerHTML = '<option value="">Selecione a Categoria</option>';
        categorias.forEach(cat => {
            selectCategoria.innerHTML += `<option value="${cat.id}">${cat.nome_categoria}</option>`;
        });
    } catch (err) {
        console.error("Erro ao carregar metadados:", err);
    }
}

// 2. Carrega e renderiza a lista de transações e o resumo
async function carregarTransacoes() {
    try {
        const res = await fetch('/api/transacoes');
        const transacoes = await res.json();
        renderizarTabela(transacoes);
        atualizarResumo(transacoes);
    } catch (err) {
        console.error("Erro ao buscar transações:", err);
    }
}

/* ---------- Funções de Interface ---------- */

function renderizarTabela(transacoes) {
    const tbody = document.querySelector("#transaction-table tbody");
    tbody.innerHTML = "";

    if (transacoes.length === 0) {
        document.getElementById("no-transactions-message").style.display = "block";
        return;
    }
    document.getElementById("no-transactions-message").style.display = "none";

    transacoes.forEach(t => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${t.id}</td>
            <td>${t.data}</td>
            <td>${t.descricao}</td>
            <td class="${t.valor < 0 ? 'value-expense' : 'value-income'}">
                ${t.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            </td>
            <td>${t.categoria}</td> 
            <td>${t.conta}</td>
            <td>
                <button class="btn-action edit" onclick="prepararEdicaoTransacao(${t.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-action delete" onclick="excluirTransacao(${t.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function atualizarResumo(dados) {
    let receitas = 0;
    let despesas = 0;

    dados.forEach(t => {
        if (t.valor > 0) receitas += t.valor;
        else despesas += Math.abs(t.valor);
    });

    const saldo = receitas - despesas;

    labelReceitas.innerText = receitas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    labelDespesas.innerText = despesas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    labelSaldo.innerText = saldo.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

/* ---------- Ações do Usuário ---------- */

// Salvar Nova Transação
transactionForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const novaTransacao = {
        data: document.getElementById("data").value,
        descricao: document.getElementById("descricao").value,
        valor: parseFloat(document.getElementById("valor").value),
        id_conta: parseInt(selectConta.value),
        id_categoria: parseInt(selectCategoria.value),
        tipo: document.getElementById("tipo").value
    };

    if (novaTransacao.tipo === "Despesa" && novaTransacao.valor > 0) {
        novaTransacao.valor *= -1;
    }

    try {
        const res = await fetch('/api/transacoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(novaTransacao)
        });

        if (res.ok) {
            document.getElementById("descricao").value = "";
            document.getElementById("valor").value = "";
            document.getElementById("tipo").value = "";
            document.getElementById("descricao").focus();

            carregarTransacoes();
            alert("Transação adicionada com sucesso!");
        }
    } catch (err) {
        alert("Erro ao salvar transação");
    }
});

// Excluir Transação
async function excluirTransacao(id) {
    if (!confirm("Deseja realmente excluir esta transação?")) return;

    try {
        const res = await fetch(`/api/transacoes/${id}`, { method: 'DELETE' });
        if (res.ok) carregarTransacoes();
    } catch (err) {
        alert("Erro ao excluir");
    }
}

/* ---------- Lógica do Modal de Edição ---------- */

async function prepararEdicaoTransacao(id) {
    const modal = document.getElementById('modal-edit');
    const container = document.getElementById('edit-fields');

    try {
        // Busca dados atuais, contas e categorias para montar os selects no modal
        const [resT, resContas, resCats] = await Promise.all([
            fetch('/api/transacoes'),
            fetch('/api/contas'),
            fetch('/api/categorias')
        ]);

        const transacoes = await resT.json();
        const contas = await resContas.json();
        const categorias = await resCats.json();

        const t = transacoes.find(item => item.id === id);

        if (t) {
            document.getElementById('edit-id').value = t.id;
            const tipoAtual = t.valor < 0 ? "Despesa" : "Receita";

            container.innerHTML = `
                <div class="input-group">
                    <label>Descrição</label>
                    <input type="text" id="edit-descricao" value="${t.descricao}" required>
                </div>
                <div class="input-group">
                    <label>Valor</label>
                    <input type="number" id="edit-valor" step="0.01" value="${Math.abs(t.valor)}" required>
                </div>
                <div class="input-group">
                    <label>Tipo</label>
                    <select id="edit-tipo" required>
                        <option value="Receita" ${tipoAtual === 'Receita' ? 'selected' : ''}>Receita</option>
                        <option value="Despesa" ${tipoAtual === 'Despesa' ? 'selected' : ''}>Despesa</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Conta</label>
                    <select id="edit-id-conta" required>
                        ${contas.map(c => `<option value="${c.id}" ${c.nome_instituicao === t.conta ? 'selected' : ''}>${c.nome_instituicao}</option>`).join('')}
                    </select>
                </div>
                <div class="input-group">
                    <label>Categoria</label>
                    <select id="edit-id-categoria" required>
                        ${categorias.map(cat => `<option value="${cat.id}" ${cat.nome_categoria === t.categoria ? 'selected' : ''}>${cat.nome_categoria}</option>`).join('')}
                    </select>
                </div>
                <div class="input-group">
                    <label>Data</label>
                    <input type="date" id="edit-data" value="${t.data}" required>
                </div>
            `;
            modal.style.display = 'flex';
        }
    } catch (err) {
        console.error("Erro ao preparar edição:", err);
    }
}

// Evento de salvar a edição
document.getElementById('form-edit').addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('edit-id').value;
    let valor = parseFloat(document.getElementById('edit-valor').value);
    const tipo = document.getElementById('edit-tipo').value;

    // Ajusta o sinal do valor conforme o tipo selecionado
    if (tipo === "Despesa" && valor > 0) valor *= -1;
    else if (tipo === "Receita" && valor < 0) valor = Math.abs(valor);

    const dadosAtualizados = {
        data: document.getElementById('edit-data').value,
        descricao: document.getElementById('edit-descricao').value,
        valor: valor,
        id_conta: parseInt(document.getElementById('edit-id-conta').value),
        id_categoria: parseInt(document.getElementById('edit-id-categoria').value)
    };

    try {
        const res = await fetch(`/api/transacoes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dadosAtualizados)
        });

        if (res.ok) {
            fecharModal();
            await carregarTransacoes();
            alert("Atualizado com sucesso!");
        } else {
            const erro = await res.json();
            alert("Erro ao salvar: " + (erro.mensagem || "Erro desconhecido"));
        }
    } catch (err) {
        alert("Erro de conexão com o servidor.");
    }
});

function fecharModal() {
    document.getElementById('modal-edit').style.display = 'none';
}

// Ação de Salvar Nova Conta
document.getElementById('form-conta').addEventListener('submit', async (e) => {
    e.preventDefault();
    const dados = {
        nome: document.getElementById('conta-nome').value,
        moeda: document.getElementById('conta-moeda').value,
        saldo: parseFloat(document.getElementById('conta-saldo').value),
        tipo: document.getElementById('conta-tipo').value
    };

    try {
        const res = await fetch('/api/contas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });
        if (res.ok) {
            alert("Conta cadastrada com sucesso!");
            e.target.reset(); // Limpa o formulário
            carregarMetadados(); // Atualiza os selects de conta na página
        }
    } catch (err) {
        alert("Erro ao conectar com o servidor.");
    }
});

// Ação de Salvar Nova Categoria
document.getElementById('form-categoria').addEventListener('submit', async (e) => {
    e.preventDefault();
    const dados = {
        nome: document.getElementById('cat-nome').value,
        tipo: document.getElementById('cat-tipo').value
    };

    try {
        const res = await fetch('/api/categorias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });
        if (res.ok) {
            alert("Categoria cadastrada com sucesso!");
            e.target.reset(); // Limpa o formulário
            carregarMetadados(); // Atualiza os selects de categoria na página
        }
    } catch (err) {
        alert("Erro ao conectar com o servidor.");
    }
});

/* ---------- Inicialização ---------- */

document.addEventListener("DOMContentLoaded", () => {
    carregarMetadados();
    carregarTransacoes();
});