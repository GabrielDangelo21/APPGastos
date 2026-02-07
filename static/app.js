"use strict";

const transactionForm = document.getElementById("transaction-form");
const selectConta = document.getElementById("conta");
const selectCategoria = document.getElementById("categoria");
let transacoesGlobais = [];

/* ---------- Funções de Carga ---------- */

/* ---------- 1. CORREÇÃO: Carregar Contas e Categorias nos Selects ---------- */
async function carregarMetadados() {
    try {
        // Busca as Contas do Python
        const resContas = await fetch('/api/contas');
        const contas = await resContas.json();
        const selectContas = document.getElementById('conta'); // ID correto do HTML

        if (selectContas) {
            selectContas.innerHTML = '<option value="">Selecione a Conta</option>';
            contas.forEach(c => {
                selectContas.innerHTML += `<option value="${c.id}">${c.nome_instituicao} (${c.moeda})</option>`;
            });
        }

        // Busca as Categorias do Python
        const resCats = await fetch('/api/categorias');
        const categorias = await resCats.json();
        const selectCats = document.getElementById('categoria'); // ID correto do HTML

        if (selectCats) {
            selectCats.innerHTML = '<option value="">Selecione a Categoria</option>';
            categorias.forEach(cat => {
                selectCats.innerHTML += `<option value="${cat.id}">${cat.nome_categoria}</option>`;
            });
        }
    } catch (err) {
        console.error("Erro ao carregar metadados:", err);
    }
}

/* ---------- 2. NOVO: Listener para Salvar Nova Conta ---------- */
const formConta = document.getElementById('form-conta');
if (formConta) {
    formConta.addEventListener('submit', async (e) => {
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
                alert("✅ Conta cadastrada com sucesso!");
                formConta.reset();
                await carregarMetadados(); // Atualiza a lista no formulário de transações
            } else {
                alert("❌ Erro ao salvar conta.");
            }
        } catch (err) {
            console.error("Erro:", err);
        }
    });
}

/* ---------- 3. NOVO: Listener para Salvar Nova Categoria ---------- */
const formCategoria = document.getElementById('form-categoria');
if (formCategoria) {
    formCategoria.addEventListener('submit', async (e) => {
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
                alert("✅ Categoria cadastrada!");
                formCategoria.reset();
                await carregarMetadados();
            } else {
                alert("❌ Erro ao salvar categoria.");
            }
        } catch (err) {
            console.error("Erro:", err);
        }
    });
}

async function carregarTransacoes() {
    try {
        const res = await fetch('/api/transacoes');
        const transacoes = await res.json();

        // ESSENCIAL: Guardamos os dados na variável global para os modais usarem
        transacoesGlobais = transacoes;

        // Atualizamos apenas os cards de resumo (o que você vê na home)
        atualizarResumo(transacoes);

        // A tabela principal não é chamada aqui para manter a home limpa
        // Mas os dados estão prontos para quando você clicar nos cards!
    } catch (err) {
        console.error("Erro ao buscar transações:", err);
    }
}

/* ---------- Listagem de Contas Corrigida ---------- */

async function listarTodasContas() {
    // 1. PRIMEIRO abrimos o modal para o usuário não achar que travou
    const modal = document.getElementById('modal-contas');
    if (modal) modal.style.display = 'flex';

    try {
        const res = await fetch('/api/contas');
        const contas = await res.json();

        const tbody = document.getElementById('body-contas');
        if (!tbody) return;
        tbody.innerHTML = "";

        contas.forEach(c => {
            const idReal = c.id;
            const saldoInicial = parseFloat(c.saldo_inicial || 0);

            // CÁLCULO SEGURO: Se transacoesGlobais não existir, o saldo é apenas o inicial
            let somaTransacoes = 0;
            if (window.transacoesGlobais && Array.isArray(window.transacoesGlobais)) {
                somaTransacoes = window.transacoesGlobais
                    .filter(t => t.id_conta == idReal)
                    .reduce((acc, t) => acc + parseFloat(t.valor || 0), 0);
            }

            const saldoTotal = saldoInicial + somaTransacoes;

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${c.id}</td>
                <td>${c.nome_instituicao}</td>
                <td><span class="currency-badge">${c.moeda}</span></td>
                <td style="text-align: right;">${saldoTotal.toFixed(2)}</td>
                <td>
                    <button class="btn-action edit" onclick="abrirModalEditarConta(${c.id}, '${c.nome_instituicao}', '${c.moeda}', ${c.saldo_inicial}, '${c.tipo_conta}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action delete" onclick="excluirConta(${c.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Erro ao carregar lista de contas:", err);
    }
}

async function salvarNovaConta(event) {
    if (event) event.preventDefault(); // Impede a página de dar refresh

    const dados = {
        nome: document.getElementById('nome_instituicao').value,
        moeda: document.getElementById('moeda_conta').value,
        saldo: document.getElementById('saldo_inicial').value,
        tipo: document.getElementById('tipo_conta').value
    };

    try {
        const res = await fetch('/api/contas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            alert("Conta salva com sucesso!");
            fecharModalCadastroConta(); // Feche seu modal de cadastro
            await listarTodasContas();  // Recarrega a lista na tela
        } else {
            const erro = await res.json();
            alert("Erro do servidor: " + erro.erro);
        }
    } catch (err) {
        console.error("Erro na requisição:", err);
    }
}

/* ---------- Listagem de Categorias Corrigida ---------- */

async function listarTodasCategorias() {
    try {
        const res = await fetch('/api/categorias');
        const categorias = await res.json();
        const modal = document.getElementById('modal-categorias');
        const tbody = document.getElementById('body-categorias');

        if (!modal || !tbody) return;

        tbody.innerHTML = "";
        categorias.forEach(cat => {
            const tr = document.createElement("tr"); // CRIA A LINHA
            tr.innerHTML = `
                <td>${cat.id}</td>
                <td>${cat.nome_categoria}</td>
                <td>
                    <button class="btn-action delete" onclick="excluirCategoria(${cat.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        modal.style.display = 'flex';
    } catch (err) { console.error(err); }
}

/* --- Abre o modal e preenche os campos com os dados atuais --- */
function abrirModalEditarConta(id, nome, moeda, saldo, tipo) {
    document.getElementById('edit-conta-id').value = id;
    document.getElementById('edit-conta-nome').value = nome;
    document.getElementById('edit-conta-moeda').value = moeda;
    document.getElementById('edit-conta-saldo').value = saldo;
    document.getElementById('edit-conta-tipo').value = tipo;

    document.getElementById('modal-edit-conta').style.display = 'flex';
}

function fecharModalEditConta() {
    document.getElementById('modal-edit-conta').style.display = 'none';
}

/* --- Escutador para o formulário de edição --- */
const formEditConta = document.getElementById('form-edit-conta');
if (formEditConta) {
    formEditConta.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-conta-id').value;

        const dados = {
            nome: document.getElementById('edit-conta-nome').value,
            moeda: document.getElementById('edit-conta-moeda').value,
            saldo: parseFloat(document.getElementById('edit-conta-saldo').value),
            tipo: document.getElementById('edit-conta-tipo').value
        };

        try {
            const res = await fetch(`/api/contas/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            if (res.ok) {
                alert("✅ Conta atualizada com sucesso!");
                fecharModalEditConta();
                location.reload(); // Recarrega para atualizar saldos e nomes
            } else {
                alert("❌ Erro ao atualizar conta.");
            }
        } catch (err) {
            console.error("Erro na requisição:", err);
        }
    });
}
/* ---------- Funções de Exclusão com Atualização de Saldo ---------- */
async function excluirConta(id) {
    if (!confirm("Tem certeza que deseja excluir esta conta?")) return;

    try {
        const res = await fetch(`/api/contas/${id}`, { method: 'DELETE' });
        const resultado = await res.json();

        if (res.ok) {
            alert("✅ Conta excluída com sucesso!");
            listarTodasContas();
        } else {
            // Aqui ele vai exibir a mensagem de "Bloqueado" que definimos no Python
            alert("⚠️ " + resultado.erro);
        }
    } catch (err) {
        alert("Erro na conexão com o servidor.");
    }
}
async function excluirCategoria(id) {
    if (confirm("Excluir categoria?")) {
        await fetch(`/api/categorias/${id}`, { method: 'DELETE' });
        listarTodasCategorias(); // Atualiza a lista do modal
        carregarMetadados();     // Atualiza o select do formulário
        carregarTransacoes();   // ATUALIZA O SALDO NOS CARDS
    }
}

// Funções para fechar esses modais específicos
function fecharModalContas() {
    document.getElementById('modal-contas').style.display = 'none';
}

function fecharModalCategorias() {
    document.getElementById('modal-categorias').style.display = 'none';
}
/* ---------- Interface ---------- */

function renderizarTabela(transacoes) {
    const tbody = document.querySelector("#transaction-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (transacoes.length === 0) {
        document.getElementById("no-transactions-message").style.display = "block";
        return;
    }
    document.getElementById("no-transactions-message").style.display = "none";

    transacoes.forEach(t => {
        const tr = document.createElement("tr");
        const moedaTransacao = t.moeda || 'BRL';

        tr.innerHTML = `
            <td>${t.id}</td>
            <td>${t.data}</td>
            <td>${t.descricao}</td>
            <td class="${t.valor < 0 ? 'value-expense' : 'value-income'}">
                ${t.valor.toLocaleString('pt-BR', { style: 'currency', currency: moedaTransacao })}
            </td>
            <td>${t.categoria}</td> 
            <td>${t.conta}</td>
            <td>
                <button onclick="prepararEdicaoTransacao(${t.id}, '${t.data}', '${t.descricao}', ${t.valor}, ${t.id_conta}, ${t.id_categoria})" class="btn-action edit">
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
    console.log("Dados recebidos para o resumo:", dados); // ADICIONE ISSO PARA TESTAR
    const container = document.getElementById("resumo-container");
    if (!container) return;
    container.innerHTML = "";

    const moedas = {};
    dados.forEach(t => {
        const m = t.moeda || 'BRL';
        if (!moedas[m]) moedas[m] = { receitas: 0, despesas: 0 };
        if (t.valor > 0) moedas[m].receitas += t.valor;
        else moedas[m].despesas += Math.abs(t.valor);
    });

    Object.keys(moedas).forEach(m => {
        const r = moedas[m];
        const saldo = r.receitas - r.despesas;

        const cardHtml = `
            <div class="currency-card" onclick="abrirDetalhesMoeda('${m}')">
                <div class="card-header">
                    <span class="currency-badge">${m}</span>
                    <h3>Extrato Resumido</h3>
                </div>
                
                <div class="card-body">
                    <div class="stat-row">
                        <div class="stat-group-left">
                            <div class="icon-circle income"><i class="fas fa-arrow-up"></i></div>
                            <label>Receitas</label>
                        </div>
                        <span class="value-income">${r.receitas.toLocaleString('pt-BR', { style: 'currency', currency: m })}</span>
                    </div>

                    <div class="stat-row">
                        <div class="stat-group-left">
                            <div class="icon-circle expense"><i class="fas fa-arrow-down"></i></div>
                            <label>Despesas</label>
                        </div>
                        <span class="value-expense">${r.despesas.toLocaleString('pt-BR', { style: 'currency', currency: m })}</span>
                    </div>

                    <div class="balance-footer">
                        <label>SALDO ATUAL EM ${m}</label>
                        <span class="${saldo >= 0 ? 'value-income' : 'value-expense'}">
                            ${saldo.toLocaleString('pt-BR', { style: 'currency', currency: m })}
                        </span>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += cardHtml;
    });
}

/* ---------- Detalhes e Modais ---------- */

function abrirDetalhesMoeda(moeda) {
    const modal = document.getElementById('modal-detalhes');
    const titulo = document.getElementById('detalhe-titulo-moeda');
    const tbody = document.getElementById('body-detalhes');

    if (!modal) return;

    titulo.innerText = `Extrato Detalhado - ${moeda}`;
    tbody.innerHTML = "";

    const filtradas = transacoesGlobais.filter(t => (t.moeda || 'BRL') === moeda);

    filtradas.forEach(t => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${t.data}</td>
            <td>${t.descricao}</td>
            <td class="${t.valor < 0 ? 'value-expense' : 'value-income'}">
                ${t.valor.toLocaleString('pt-BR', { style: 'currency', currency: moeda })}
            </td>
            <td>${t.categoria}</td>
        `;
        tbody.appendChild(tr);
    });

    modal.style.display = 'flex';
}

function fecharModalDetalhes() {
    document.getElementById('modal-detalhes').style.display = 'none';
}

/* ---------- Ações Form ---------- */

transactionForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Captura a data selecionada e a data de hoje (formato YYYY-MM-DD)
    const dataInput = document.getElementById("data").value;
    const hoje = new Date().toISOString().split("T")[0];

    // BLOQUEIO: Se a data for maior que hoje, exibe alerta e para a execução
    if (dataInput > hoje) {
        alert("Atenção: Não é possível lançar transações em datas futuras!");
        return;
    }

    const valorRaw = parseFloat(document.getElementById("valor").value);
    const tipo = document.getElementById("tipo").value;

    const dados = {
        data: dataInput,
        descricao: document.getElementById("descricao").value,
        valor: tipo === "Despesa" ? -Math.abs(valorRaw) : Math.abs(valorRaw),
        id_conta: parseInt(selectConta.value),
        id_categoria: parseInt(selectCategoria.value)
    };

    try {
        const res = await fetch('/api/transacoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            transactionForm.reset();
            // Garante que o limite de data continue ativo após resetar o form
            document.getElementById("data").setAttribute("max", hoje);
            await carregarTransacoes();
            alert("Transação salva com sucesso!");
        } else {
            alert("Erro ao salvar transação no servidor.");
        }
    } catch (err) {
        console.error("Erro na requisição:", err);
        alert("Erro de conexão.");
    }
});


async function excluirTransacao(id) {
    if (confirm("Excluir?")) {
        await fetch(`/api/transacoes/${id}`, { method: 'DELETE' });
        carregarTransacoes();
    }
}

/* ---------- Edição ---------- */

async function prepararEdicaoTransacao(id, data, descricao, valor, id_conta, id_categoria) {
    const modal = document.getElementById('modal-edit');
    const container = document.getElementById('edit-fields');
    document.getElementById('modal-title').innerText = "Editar Transação";
    document.getElementById('edit-id').value = id;

    modal.style.display = 'flex';
    container.innerHTML = "Carregando...";

    const [resContas, resCats] = await Promise.all([fetch('/api/contas'), fetch('/api/categorias')]);
    const contas = await resContas.json();
    const categorias = await resCats.json();

    container.innerHTML = `
        <input type="hidden" id="edit-target" value="transacao">
        <div class="input-group"><label>Data</label><input type="date" id="edit-data" value="${data}"></div>
        <div class="input-group"><label>Descrição</label><input type="text" id="edit-descricao" value="${descricao}"></div>
        <div class="input-group"><label>Valor</label><input type="number" step="0.01" id="edit-valor" value="${Math.abs(valor)}"></div>
        <div class="input-group">
            <label>Tipo</label>
            <select id="edit-tipo">
                <option value="Receita" ${valor >= 0 ? 'selected' : ''}>Receita</option>
                <option value="Despesa" ${valor < 0 ? 'selected' : ''}>Despesa</option>
            </select>
        </div>
        <div class="input-group">
            <label>Conta</label>
            <select id="edit-id-conta">
                ${contas.map(c => `<option value="${c.id}" ${String(c.id) == String(id_conta) ? 'selected' : ''}>${c.nome_instituicao}</option>`).join('')}
            </select>
        </div>
        <div class="input-group">
            <label>Categoria</label>
            <select id="edit-id-categoria">
                ${categorias.map(cat => `<option value="${cat.id}" ${String(cat.id) == String(id_categoria) ? 'selected' : ''}>${cat.nome_categoria}</option>`).join('')}
            </select>
        </div>
    `;
}

document.getElementById('form-edit').addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('edit-id').value;
    const target = document.getElementById('edit-target')?.value || "transacao";

    if (target === "transacao") {
        const dataEdit = document.getElementById('edit-data').value;
        const hoje = new Date().toISOString().split("T")[0];

        // BLOQUEIO na Edição
        if (dataEdit > hoje) {
            alert("Atenção: Não é permitido alterar a transação para uma data futura!");
            return;
        }

        const valorRaw = parseFloat(document.getElementById('edit-valor').value);
        const tipo = document.getElementById('edit-tipo').value;

        const dados = {
            data: dataEdit,
            descricao: document.getElementById('edit-descricao').value,
            valor: tipo === "Despesa" ? -Math.abs(valorRaw) : Math.abs(valorRaw),
            id_conta: parseInt(document.getElementById('edit-id-conta').value),
            id_categoria: parseInt(document.getElementById('edit-id-categoria').value)
        };

        try {
            const res = await fetch(`/api/transacoes/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            if (res.ok) {
                fecharModal();
                await carregarTransacoes();
                alert("Alteração salva com sucesso!");
            } else {
                alert("Erro ao atualizar transação.");
            }
        } catch (err) {
            console.error("Erro de conexão:", err);
            alert("Erro de conexão.");
        }
    }
});

function fecharModal() {
    document.getElementById('modal-edit').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const hoje = new Date().toISOString().split("T")[0];

    // Bloqueia o calendário do formulário principal
    if (document.getElementById("data")) {
        document.getElementById("data").setAttribute("max", hoje);
    }

    carregarMetadados();
    carregarTransacoes();
});