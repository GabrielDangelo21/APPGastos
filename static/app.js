document.addEventListener('DOMContentLoaded', () => {
    // 1. Pega a data de hoje no formato AAAA-MM-DD
    const hoje = new Date().toISOString().split('T')[0];

    // 2. Configura o input de Nova Transação
    const dataInput = document.getElementById('data');
    if (dataInput) {
        dataInput.value = hoje; // Define hoje como padrão
        dataInput.max = hoje;   // BLOQUEIA datas futuras no calendário
    }

    // 3. Configura o input de Editar Transação (para não burlarem na edição)
    const editDataInput = document.getElementById('edit-trans-data');
    if (editDataInput) {
        editDataInput.max = hoje; // BLOQUEIA datas futuras na edição também
    }

    // Carrega os dados iniciais
    carregarCategorias();
    carregarTransacoes();
});

/* --- CATEGORIAS --- */
async function carregarCategorias() {
    try {
        const res = await fetch('/api/categorias');
        const categorias = await res.json();

        const select = document.getElementById('categoria');

        // Limpa e preenche o Select
        select.innerHTML = '<option value="">Selecione...</option>';
        categorias.forEach(cat => {
            select.innerHTML += `<option value="${cat.id}">${cat.nome_categoria} (${cat.tipo})</option>`;
        });
    } catch (err) {
        console.error("Erro categorias:", err);
    }
}

// Salvar Nova Categoria (Agora no Card)
const formCat = document.getElementById('form-categoria');
if (formCat) {
    formCat.addEventListener('submit', async (e) => {
        e.preventDefault(); // Impede a página de recarregar
        console.log("Tentando salvar categoria...");

        // Pega os valores pelos IDs que definimos no HTML acima
        const nomeInput = document.getElementById('cat-nome');
        const tipoInput = document.getElementById('cat-tipo');

        const dados = {
            nome: nomeInput.value,
            tipo: tipoInput.value
        };

        try {
            const res = await fetch('/api/categorias', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            if (res.ok) {
                nomeInput.value = ''; // Limpa o campo
                alert("Categoria criada com sucesso!");
                await carregarCategorias(); // Atualiza o select ao lado
            } else {
                const erro = await res.json();
                alert("Erro: " + erro.erro);
            }
        } catch (err) {
            console.error(err);
            alert("Erro de conexão ao salvar categoria.");
        }
    });
}



/* --- TRANSAÇÕES (MANTIDO IGUAL) --- */
let transacoesGlobais = []; // Variável para guardar os dados e filtrar depois

async function carregarTransacoes() {
    try {
        const res = await fetch('/api/transacoes');
        transacoesGlobais = await res.json();

        let despesasBRL = 0;
        let despesasEUR = 0;

        transacoesGlobais.forEach(t => {
            const val = parseFloat(t.valor);
            if (val < 0) { // Apenas despesas
                if (t.moeda === 'BRL') despesasBRL += Math.abs(val);
                else if (t.moeda === 'EUR') despesasEUR += Math.abs(val);
            }
        });

        document.getElementById('total-despesas-brl').innerText = `R$ ${despesasBRL.toFixed(2)}`;
        document.getElementById('total-despesas-eur').innerText = `${despesasEUR.toFixed(2)} €`;

    } catch (err) { console.error(err); }
}

// Função para abrir o modal filtrado
function abrirModalTransacoesMoeda(moeda) {
    const modal = document.getElementById('modal-transacoes-moeda');
    const titulo = document.getElementById('titulo-modal-moeda');
    const corpo = document.getElementById('corpo-tabela-moeda');

    titulo.innerText = `Despesas em ${moeda}`;
    corpo.innerHTML = '';

    // Filtra apenas as despesas da moeda clicada
    const filtradas = transacoesGlobais.filter(t => t.moeda === moeda && t.valor < 0);

    if (filtradas.length === 0) {
        corpo.innerHTML = '<tr><td colspan="5" style="padding:20px; text-align:center;">Nenhuma despesa encontrada.</td></tr>';
    } else {
        filtradas.forEach(t => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid var(--border)';

            // Aqui garantimos que os botões sejam desenhados
            tr.innerHTML = `
                <td style="padding: 10px;">${new Date(t.data).toLocaleDateString('pt-BR')}</td>
                <td>${t.descricao}</td>
                <td><span class="badge badge-despesa">${t.categoria}</span></td>
                <td style="color: #FF6B6B;">
                    ${moeda === 'BRL' ? 'R$' : '€'} ${Math.abs(t.valor).toFixed(2)}
                </td>
                <td style="text-align: right;">
                    <button class="btn-action edit" onclick="fecharEEditar(${JSON.stringify(t).replace(/"/g, '&quot;')})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action delete" onclick="excluirTransacao(${t.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            corpo.appendChild(tr);
        });
    }
    modal.style.display = 'flex';
}
// Função auxiliar para fechar o modal de lista antes de abrir o de edição
function fecharEEditar(transacao) {
    document.getElementById('modal-transacoes-moeda').style.display = 'none';
    prepararEdicaoTransacao(transacao);
}

/* --- SALVAR NOVA TRANSAÇÃO --- */
const formTrans = document.getElementById('form-transacao');
if (formTrans) {
    formTrans.addEventListener('submit', async (e) => {
        e.preventDefault();

        // --- NOVA VALIDAÇÃO DE DATA FUTURA ---
        const inputData = document.getElementById('data').value;
        const hoje = new Date().toISOString().split('T')[0];

        if (inputData > hoje) {
            alert("⚠️ Não é permitido adicionar transações com data futura!");
            return; // Para o código aqui e não salva nada
        }
        // -------------------------------------

        console.log("Botão de transação clicado!");

        const selectCat = document.getElementById('categoria');

        // Verifica se o usuário selecionou uma categoria válida
        if (!selectCat.value) {
            alert("Selecione uma categoria!");
            return;
        }

        // Lógica para definir se é negativo (Despesa) ou positivo (Receita)
        const textoCategoria = selectCat.options[selectCat.selectedIndex].text;
        const ehDespesa = textoCategoria.includes('Despesa'); // Procura a palavra "Despesa" no texto

        let valorInput = parseFloat(document.getElementById('valor').value);
        if (ehDespesa) valorInput = -Math.abs(valorInput);
        else valorInput = Math.abs(valorInput);

        const dados = {
            data: document.getElementById('data').value,
            descricao: document.getElementById('descricao').value,
            valor: valorInput,
            moeda: document.getElementById('moeda').value,
            categoria_id: selectCat.value
        };

        try {
            const res = await fetch('/api/transacoes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            if (res.ok) {
                formTrans.reset(); // Limpa o formulário
                // Reseta a data para hoje
                document.getElementById('data').value = new Date().toISOString().split('T')[0];

                // alert("Transação adicionada!");
                await carregarTransacoes(); // Atualiza os cards de totais
            } else {
                const erro = await res.json();
                alert("Erro: " + erro.erro);
            }
        } catch (err) {
            console.error(err);
            alert("Erro de conexão ao salvar transação.");
        }
    });
}


/* --- EXCLUIR TRANSAÇÃO (COM ATUALIZAÇÃO IMEDIATA) --- */
async function excluirTransacao(id) {
    if (!confirm("Tem certeza que deseja apagar este item?")) return;

    try {
        const res = await fetch(`/api/transacoes/${id}`, { method: 'DELETE' });

        if (res.ok) {
            // 1. Atualiza os totais e baixa os dados novos do banco
            await carregarTransacoes();

            // 2. Verifica qual modal está aberto olhando o título dele
            const modal = document.getElementById('modal-transacoes-moeda');

            // Só tentamos atualizar a lista se o modal estiver visível
            if (modal.style.display === 'flex') {
                const titulo = document.getElementById('titulo-modal-moeda').innerText;

                if (titulo.includes("Extrato Completo")) {
                    abrirExtratoCompleto(); // Recarrega a lista completa
                } else if (titulo.includes("BRL")) {
                    abrirModalTransacoesMoeda('BRL'); // Recarrega só BRL
                } else if (titulo.includes("EUR")) {
                    abrirModalTransacoesMoeda('EUR'); // Recarrega só EUR
                }
            } else {
                // Se o modal estava fechado (ex: excluiu da lista principal antiga), apenas avisa
                alert("Transação excluída!");
            }

        } else {
            const erro = await res.json();
            alert("Erro: " + erro.erro);
        }
    } catch (err) {
        console.error(err);
        alert("Erro de conexão ao excluir.");
    }
}

/* --- GERENCIAMENTO DE CATEGORIAS --- */

// 1. Abrir Modal de Lista e Carregar Tabela
async function abrirModalListaCategorias() {
    const modal = document.getElementById('modal-lista-categorias');
    const tbody = document.getElementById('tabela-categorias-body');

    if (!modal || !tbody) return;

    tbody.innerHTML = '<tr><td colspan="3">Carregando...</td></tr>';
    modal.style.display = 'flex';

    try {
        const res = await fetch('/api/categorias');
        const categorias = await res.json();

        tbody.innerHTML = '';

        categorias.forEach(c => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid var(--border)';

            const badgeClass = c.tipo === 'Receita' ? 'badge-receita' : 'badge-despesa';

            tr.innerHTML = `
                <td style="padding: 10px;">${c.nome_categoria}</td>
                <td><span class="badge ${badgeClass}">${c.tipo}</span></td>
                <td style="text-align: right;">
                    <button class="btn-action edit" onclick="abrirModalEditarCategoria(${c.id}, '${c.nome_categoria}', '${c.tipo}')" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action delete" onclick="excluirCategoria(${c.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Erro ao carregar categorias:", err);
        tbody.innerHTML = '<tr><td colspan="3">Erro ao carregar lista.</td></tr>';
    }
}
// 2. Abrir Modal de Edição (Preenche os dados)
function abrirModalEditarCategoria(id, nome, tipo) {
    document.getElementById('edit-cat-id').value = id;
    document.getElementById('edit-cat-nome').value = nome;
    document.getElementById('edit-cat-tipo').value = tipo;

    // Fecha a lista e abre a edição
    document.getElementById('modal-lista-categorias').style.display = 'none';
    document.getElementById('modal-editar-categoria').style.display = 'flex';
}

// 3. Salvar Edição (PUT)
const formEditCat = document.getElementById('form-editar-categoria');
if (formEditCat) {
    formEditCat.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('edit-cat-id').value;
        const dados = {
            nome: document.getElementById('edit-cat-nome').value,
            tipo: document.getElementById('edit-cat-tipo').value
        };

        try {
            const res = await fetch(`/api/categorias/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            if (res.ok) {
                // 1. FECHA OS MODAIS
                document.getElementById('modal-editar-categoria').style.display = 'none';
                document.getElementById('modal-lista-categorias').style.display = 'none';

                // 2. ATUALIZA OS DADOS NA TELA
                await carregarCategorias();
                await carregarTransacoes();

            } else {
                alert("Erro ao editar.");
            }
        } catch (err) {
            console.error(err);
        }
    });
}

// 4. Excluir Categoria (DELETE)
async function excluirCategoria(id) {
    if (!confirm("Tem certeza? Se houver transações nesta categoria, a exclusão será bloqueada.")) return;

    try {
        const res = await fetch(`/api/categorias/${id}`, { method: 'DELETE' });

        if (res.ok) {
            // Remove a linha visualmente ou recarrega
            abrirModalListaCategorias();
            carregarCategorias(); // Atualiza o select da página principal
        } else {
            const erro = await res.json();
            alert("⚠️ " + (erro.erro || "Erro ao excluir"));
        }
    } catch (err) {
        alert("Erro de conexão.");
    }
}

/* --- EDIÇÃO DE TRANSAÇÃO --- */

// 1. Preenche o modal com os dados atuais
async function prepararEdicaoTransacao(transacao) {
    // Garantimos que o select de categorias do modal de edição esteja atualizado
    const selectPrincipal = document.getElementById('categoria');
    const selectEdit = document.getElementById('edit-trans-categoria');
    selectEdit.innerHTML = selectPrincipal.innerHTML;

    // Preenche os campos
    document.getElementById('edit-trans-id').value = transacao.id;
    document.getElementById('edit-trans-data').value = transacao.data;
    document.getElementById('edit-trans-descricao').value = transacao.descricao;
    document.getElementById('edit-trans-valor').value = Math.abs(transacao.valor);
    document.getElementById('edit-trans-moeda').value = transacao.moeda;
    document.getElementById('edit-trans-categoria').value = transacao.id_categoria;

    document.getElementById('modal-editar-transacao').style.display = 'flex';
}

// 2. Envia a atualização para o servidor
const formEditTrans = document.getElementById('form-editar-transacao');
if (formEditTrans) {
    formEditTrans.addEventListener('submit', async (e) => {
        e.preventDefault();

        // --- VALIDAÇÃO DE DATA FUTURA NA EDIÇÃO ---
        const inputData = document.getElementById('edit-trans-data').value;
        const hoje = new Date().toISOString().split('T')[0];

        if (inputData > hoje) {
            alert("⚠️ A data editada não pode ser futura!");
            return;
        }
        const id = document.getElementById('edit-trans-id').value;

        const dados = {
            data: document.getElementById('edit-trans-data').value,
            descricao: document.getElementById('edit-trans-descricao').value,
            valor: document.getElementById('edit-trans-valor').value,
            moeda: document.getElementById('edit-trans-moeda').value,
            categoria_id: document.getElementById('edit-trans-categoria').value
        };

        const res = await fetch(`/api/transacoes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            document.getElementById('modal-editar-transacao').style.display = 'none';
            carregarTransacoes(); // Recarrega a lista e os saldos
        } else {
            alert("Erro ao atualizar transação.");
        }
    });
}

/* --- EXTRATO COMPLETO (Resolve o problema das Receitas ocultas) --- */
function abrirExtratoCompleto() {
    const modal = document.getElementById('modal-transacoes-moeda');
    const titulo = document.getElementById('titulo-modal-moeda');
    const corpo = document.getElementById('corpo-tabela-moeda');

    titulo.innerHTML = '<i class="fas fa-history"></i> Extrato Completo';
    corpo.innerHTML = '';

    // Ordena por data (mais recente primeiro)
    const todas = transacoesGlobais.sort((a, b) => new Date(b.data) - new Date(a.data));

    if (todas.length === 0) {
        corpo.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px;">Nenhum registro encontrado.</td></tr>';
    } else {
        todas.forEach(t => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #333';

            const val = parseFloat(t.valor);
            const ehDespesa = val < 0;

            // Define cores e sinais visualmente
            const corValor = ehDespesa ? '#FF6B6B' : '#2ECC71'; // Vermelho ou Verde
            const badgeClass = ehDespesa ? 'badge-despesa' : 'badge-receita';

            tr.innerHTML = `
                <td style="padding: 10px;">${new Date(t.data).toLocaleDateString('pt-BR')}</td>
                <td>${t.descricao}</td>
                <td><span class="badge ${badgeClass}">${t.categoria}</span></td>
                <td style="color: ${corValor}; font-weight: bold;">
                    ${t.moeda === 'BRL' ? 'R$' : '€'} ${Math.abs(val).toFixed(2)}
                </td>
                <td style="text-align: right;">
                    <button class="btn-action edit" onclick="fecharEEditar(${JSON.stringify(t).replace(/"/g, '&quot;')})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action delete" onclick="excluirTransacao(${t.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            corpo.appendChild(tr);
        });
    }

    modal.style.display = 'flex';
}

window.onclick = function (event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = "none";
    }
}