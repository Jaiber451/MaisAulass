const state = {
    data: { usuarios: [], turmas: [], atividades: [], entregas: [] },
    filtered: {},
    report: { items: [], resumo: {} },
    editing: null,
    ready: false
};

const SETTINGS_DEFAULTS = {
    name: 'Julia',
    role: 'Gestora',
    message: 'Tudo pronto para organizar seu dia de aprendizado.',
    school: '',
    year: '2026',
    theme: 'claro',
    density: 'confortavel',
    confirmDelete: true,
    previewLimit: 3,
    showClassCards: true
};

const ROLES = ['Gestora', 'Professor', 'Coordenação', 'Responsável'];

let preferences = { ...SETTINGS_DEFAULTS };

const cfg = {
    usuarios: {
        title: 'Usuário',
        fields: [['nome', 'Nome completo', 'text', true], ['email', 'E-mail', 'email', true]],
        cols: [['nome', 'Nome'], ['email', 'E-mail']]
    },
    turmas: {
        title: 'Turma',
        fields: [
            ['nome_turma', 'Nome da turma', 'text', true],
            ['user_id', 'Responsável', 'relation', true, 'usuarios'],
            ['descricao_atividade', 'Descrição', 'text', false]
        ],
        cols: [['nome_turma', 'Turma'], ['usuario_nome', 'Responsável'], ['descricao_atividade', 'Descrição']]
    },
    atividades: {
        title: 'Atividade',
        fields: [
            ['titulo', 'Título', 'text', true],
            ['descricao_atividade', 'Descrição', 'text', false],
            ['turma_id', 'Turma', 'relation', true, 'turmas'],
            ['data_entrega', 'Data de entrega', 'date', true]
        ],
        cols: [['titulo', 'Atividade'], ['turma_nome', 'Turma'], ['data_entrega', 'Entrega']]
    },
    entregas: {
        title: 'Entrega',
        fields: [
            ['data_entrega', 'Data da entrega', 'date', true],
            ['status_entrega', 'Status', 'select', true, ['Pendente', 'Entregue', 'Atrasada']],
            ['atividade_id', 'Atividade', 'relation', true, 'atividades'],
            ['user_id', 'Usuário', 'relation', true, 'usuarios'],
            ['nota', 'Nota (0 a 10)', 'number', false]
        ],
        cols: [
            ['atividade_titulo', 'Atividade'],
            ['usuario_nome', 'Usuário'],
            ['status_entrega', 'Status'],
            ['data_entrega', 'Data'],
            ['nota', 'Nota']
        ]
    }
};

const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
}[character]));

const TOKEN_KEY = 'maisAulaToken';

async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) headers.Authorization = 'Bearer ' + token;
    const response = await fetch('/api' + path, { ...options, headers });

    let data = {};
    try {
        data = await response.json();
    } catch (_) {
        data = {};
    }

    if (response.status === 401 && path !== '/auth/login' && path !== '/auth/cadastro') {
        encerrarSessaoLocal();
    }

    if (!response.ok) {
        throw new Error(data.error || 'Não foi possível concluir a operação.');
    }

    return data;
}

function encerrarSessaoLocal() {
    localStorage.removeItem(TOKEN_KEY);
    delete document.documentElement.dataset.sessao;
    state.usuario = null;
}

async function entrarNoApp(usuario) {
    state.usuario = usuario;
    preferences = { ...preferences, name: usuario.nome };
    localStorage.setItem('maisAulaSettings', JSON.stringify(preferences));
    fillSettingsForm();
    applySettings();
    document.documentElement.dataset.sessao = 'ativa';
    await loadAll();
    await dashboard();
}

function toast(message) {
    const element = document.querySelector('#toast');
    element.textContent = message;
    element.classList.add('show');
    setTimeout(() => element.classList.remove('show'), 2600);
}

function statusClass(status) {
    if (status === 'Entregue') return 'done';
    if (status === 'Atrasada') return 'late';
    return 'wait';
}

async function loadAll() {
    const resources = Object.keys(state.data);
    const results = await Promise.all(resources.map(resource => api('/' + resource)));
    resources.forEach((resource, index) => {
        state.data[resource] = results[index];
        state.filtered[resource] = results[index];
    });

    renderDashboard();
    fillFilterOptions();
    Object.keys(cfg).forEach(renderTable);
    renderClassCards();
    await Promise.all([
        applyResourceFilter('turmas'),
        applyResourceFilter('atividades'),
        applyResourceFilter('entregas'),
        applyResourceFilter('usuarios'),
        renderReports()
    ]);
    state.ready = true;
}

async function dashboard() {
    const data = await api('/dashboard');
    const labels = [
        ['Usuários', data.usuarios, 'usuarios'],
        ['Turmas', data.turmas, 'turmas'],
        ['Atividades', data.atividades, 'atividades'],
        ['Entregas', data.entregas, 'entregas'],
        ['Pendentes', data.pendentes, 'entregas']
    ];

    document.querySelector('#summary').innerHTML = labels.map(([label, value, page]) => `
        <div class="stat dashboard-stat" data-page="${page}" role="button" tabindex="0">
            <small>${label}</small>
            <strong>${value}</strong>
        </div>
    `).join('');

    const graded = state.data.entregas.filter(item => item.nota !== null && item.nota !== undefined && item.nota !== '');
    const average = graded.length
        ? graded.reduce((sum, item) => sum + Number(item.nota), 0) / graded.length
        : null;

    document.querySelector('#performance-score').textContent = average === null
        ? '—'
        : average.toFixed(1).replace('.', ',');
    document.querySelector('#performance-label').textContent = average === null
        ? 'Aguardando entregas avaliadas'
        : `${graded.length} entrega(s) com nota`;
    document.querySelector('#performance-chart').innerHTML = graded.slice(0, 8).reverse().map(item => `
        <span style="height:${Math.max(8, Math.min(100, Number(item.nota) * 10))}%"></span>
    `).join('') || '<small class="muted">Sem notas para exibir</small>';
}

function previewCount() {
    const value = Number(preferences.previewLimit);
    if (!Number.isFinite(value)) return SETTINGS_DEFAULTS.previewLimit;
    return Math.min(6, Math.max(1, Math.round(value)));
}

function renderDashboard() {
    const limit = previewCount();
    const classes = state.data.turmas.slice(0, limit);
    document.querySelector('#classes-list').innerHTML = classes.length
        ? classes.map((item, index) => `
            <div class="schedule-item">
                <span class="bubble ${['purple', 'green', 'orange'][index % 3]}">▧</span>
                <div><b>${esc(item.nome_turma)}</b><small>${esc(item.usuario_nome || 'Responsável')}</small></div>
                <span class="schedule-time">Turma</span>
            </div>
        `).join('')
        : '<div class="empty">Nenhuma turma cadastrada.</div>';

    const activities = state.data.atividades.slice(0, limit);
    document.querySelector('#activities-list').innerHTML = activities.length
        ? activities.map((item, index) => `
            <div class="activity-item">
                <span class="bubble ${['purple', 'orange', 'green'][index % 3]}">▤</span>
                <div><b>${esc(item.titulo)}</b><small>${esc(item.turma_nome || 'Sem turma')}</small></div>
                <span class="deadline">${esc(item.data_entrega)}</span>
            </div>
        `).join('')
        : '<div class="empty">Nenhuma atividade cadastrada.</div>';

    const deliveries = state.data.entregas.slice(0, limit);
    document.querySelector('#recent-deliveries').innerHTML = deliveries.length
        ? deliveries.map(item => `
            <div class="delivery">
                <span class="bubble blue">✓</span>
                <div><b>${esc(item.atividade_titulo)}</b><small>${esc(item.usuario_nome)}</small></div>
                <span class="status ${statusClass(item.status_entrega)}">${esc(item.status_entrega)}</span>
            </div>
        `).join('')
        : '<div class="empty">Nenhuma entrega cadastrada.</div>';
}

function fillFilterOptions() {
    const responsible = document.querySelector('#turmas-responsavel');
    if (responsible) {
        const selected = responsible.value;
        responsible.innerHTML = '<option value="">Todos os responsáveis</option>' + state.data.usuarios.map(user => `
            <option value="${user.id}">${esc(user.nome)}</option>
        `).join('');
        responsible.value = selected;
    }

    const activity = document.querySelector('#relatorios-atividade');
    if (activity) {
        const selected = activity.value;
        activity.innerHTML = '<option value="">Todas as atividades</option>' + state.data.atividades.map(item => `
            <option value="${item.id}">${esc(item.titulo)}</option>
        `).join('');
        activity.value = selected;
    }
}

function getFiltered(type) {
    return state.filtered[type] ?? state.data[type] ?? [];
}

function renderClassCards() {
    const box = document.querySelector('#turmas-cards');
    if (!preferences.showClassCards) {
        box.hidden = true;
        box.innerHTML = '';
        return;
    }
    box.hidden = false;
    const rows = getFiltered('turmas');
    box.innerHTML = rows.map(item => `
        <article class="class-card">
            <h3>${esc(item.nome_turma)}</h3>
            <p>${esc(item.descricao_atividade || 'Turma cadastrada na plataforma')}</p>
            <span class="students">Responsável: ${esc(item.usuario_nome || 'Não informado')}</span>
        </article>
    `).join('') || '<div class="panel empty">Nenhuma turma encontrada.</div>';
}

function renderTable(type) {
    const rows = getFiltered(type);
    const config = cfg[type];
    const target = document.querySelector('#' + type + '-table');
    target.innerHTML = `
        <table class="data">
            <thead><tr>${config.cols.map(column => `<th>${column[1]}</th>`).join('')}<th>Ações</th></tr></thead>
            <tbody>
                ${rows.map(item => `
                    <tr>
                        ${config.cols.map(column => `<td>${esc(item[column[0]] ?? '—')}</td>`).join('')}
                        <td>
                            <button class="action" onclick="openForm('${type}', ${item.id})">Editar</button>
                            <button class="action danger" onclick="removeItem('${type}', ${item.id})">Excluir</button>
                        </td>
                    </tr>
                `).join('') || `<tr><td colspan="${config.cols.length + 1}">Nenhum registro encontrado.</td></tr>`}
            </tbody>
        </table>
    `;
}

function queryString(values) {
    const params = new URLSearchParams();
    Object.entries(values).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') params.set(key, value);
    });
    const query = params.toString();
    return query ? '?' + query : '';
}

async function applyResourceFilter(type) {
    const values = {};
    if (type === 'turmas') {
        values.user_id = document.querySelector('#turmas-responsavel').value;
    } else if (type === 'atividades') {
        values.data_inicio = document.querySelector('#atividades-data-inicio').value;
        values.data_fim = document.querySelector('#atividades-data-fim').value;
    } else if (type === 'entregas') {
        values.status = document.querySelector('#entregas-status').value;
        values.data_inicio = document.querySelector('#entregas-data-inicio').value;
        values.data_fim = document.querySelector('#entregas-data-fim').value;
    } else if (type === 'usuarios') {
        values.nome = document.querySelector('#usuarios-nome').value.trim();
    }

    try {
        state.filtered[type] = await api('/' + type + queryString(values));
        renderTable(type);
        if (type === 'turmas') renderClassCards();
    } catch (error) {
        toast(error.message);
    }
}

async function renderReports() {
    const activityId = document.querySelector('#relatorios-atividade')?.value || '';
    try {
        state.report = await api('/relatorios' + queryString({ atividade_id: activityId }));
    } catch (error) {
        toast(error.message);
        return;
    }

    const summary = state.report.resumo;
    const cards = [
        ['Total de entregas', summary.total],
        ['Concluídas', summary.concluidas],
        ['Atrasadas', summary.atrasadas],
        ['Média geral', summary.media === null ? '—' : Number(summary.media).toFixed(1).replace('.', ',')]
    ];
    document.querySelector('#report-cards').innerHTML = cards.map(([label, value]) => `
        <div class="stat"><small>${label}</small><strong>${value}</strong></div>
    `).join('');

    const columns = cfg.entregas.cols;
    document.querySelector('#report-table').innerHTML = `
        <table class="data">
            <thead><tr>${columns.map(column => `<th>${column[1]}</th>`).join('')}</tr></thead>
            <tbody>
                ${state.report.items.map(item => `
                    <tr>${columns.map(column => `<td>${esc(item[column[0]] ?? '—')}</td>`).join('')}</tr>
                `).join('') || `<tr><td colspan="${columns.length}">Nenhuma entrega encontrada.</td></tr>`}
            </tbody>
        </table>
    `;
}

function clearFilters(type) {
    const fields = {
        turmas: ['#turmas-responsavel'],
        atividades: ['#atividades-data-inicio', '#atividades-data-fim'],
        entregas: ['#entregas-status', '#entregas-data-inicio', '#entregas-data-fim'],
        usuarios: ['#usuarios-nome'],
        relatorios: ['#relatorios-atividade']
    }[type] || [];

    fields.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) element.value = '';
    });

    if (type === 'relatorios') {
        renderReports();
    } else {
        applyResourceFilter(type);
    }
}

function bindFilters() {
    const filters = [
        ['turmas-responsavel', 'turmas', 'change'],
        ['atividades-data-inicio', 'atividades', 'change'],
        ['atividades-data-fim', 'atividades', 'change'],
        ['entregas-status', 'entregas', 'change'],
        ['entregas-data-inicio', 'entregas', 'change'],
        ['entregas-data-fim', 'entregas', 'change'],
        ['usuarios-nome', 'usuarios', 'input']
    ];

    filters.forEach(([id, type, eventName]) => {
        const element = document.querySelector('#' + id);
        if (element) element.addEventListener(eventName, () => applyResourceFilter(type));
    });

    document.querySelector('#relatorios-atividade').addEventListener('change', renderReports);
}

function relationOptions(source, current) {
    const rows = state.data[source] || [];
    const labels = { usuarios: 'nome', turmas: 'nome_turma', atividades: 'titulo' };
    return '<option value="">Selecione...</option>' + rows.map(item => `
        <option value="${item.id}" ${Number(current) === Number(item.id) ? 'selected' : ''}>${esc(item[labels[source]])}</option>
    `).join('');
}

function openPage(id) {
    document.querySelectorAll('.page').forEach(page => page.classList.toggle('active', page.id === id));
    document.querySelectorAll('.nav[data-page]').forEach(button => button.classList.toggle('active', button.dataset.page === id));
    if (id === 'dashboard') dashboard();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function bindDashboardLinks() {
    document.querySelectorAll('.dashboard-link[data-page]').forEach(element => {
        element.addEventListener('click', event => {
            if (event.target.closest('a, button')) return;
            openPage(element.dataset.page);
        });
        element.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openPage(element.dataset.page);
            }
        });
    });

    const summary = document.querySelector('#summary');
    summary.addEventListener('click', event => {
        const card = event.target.closest('.stat[data-page]');
        if (card) openPage(card.dataset.page);
    });
    summary.addEventListener('keydown', event => {
        const card = event.target.closest('.stat[data-page]');
        if (card && (event.key === 'Enter' || event.key === ' ')) {
            event.preventDefault();
            openPage(card.dataset.page);
        }
    });
}

document.querySelectorAll('.nav[data-page]').forEach(button => {
    button.onclick = () => openPage(button.dataset.page);
});

function openForm(type, id = null) {
    const row = id ? state.data[type].find(item => item.id === id) : null;
    state.editing = { type, id };
    document.querySelector('#modal-title').textContent = (row ? 'Editar ' : 'Novo ') + cfg[type].title;

    document.querySelector('#fields').innerHTML = cfg[type].fields.map(([name, label, kind, required, extra]) => {
        let control;
        if (kind === 'select') {
            control = `<select name="${name}" ${required ? 'required' : ''}>${extra.map(option => `
                <option ${row?.[name] === option ? 'selected' : ''}>${option}</option>
            `).join('')}</select>`;
        } else if (kind === 'relation') {
            control = `<select name="${name}" ${required ? 'required' : ''}>${relationOptions(extra, row?.[name])}</select>`;
        } else {
            let constraints = '';
            if (name === 'nota') constraints = 'min="0" max="10" step="0.1"';
            if (name === 'nome') constraints = 'minlength="3" maxlength="100"';
            if (name === 'email') constraints = 'maxlength="100"';
            control = `<input name="${name}" type="${kind}" ${constraints} value="${esc(row?.[name] ?? '')}" ${required ? 'required' : ''}>`;
        }
        return `<div class="field"><label>${label}</label>${control}</div>`;
    }).join('');

    document.querySelector('#modal').classList.remove('hidden');
}

function closeModal() {
    document.querySelector('#modal').classList.add('hidden');
}

document.querySelector('#form').onsubmit = async event => {
    event.preventDefault();
    const { type, id } = state.editing;
    const payload = {};

    for (const [name, , kind] of cfg[type].fields) {
        let value = new FormData(event.target).get(name);
        if ((kind === 'number' || kind === 'relation') && value !== '') value = Number(value);
        if (value !== '') payload[name] = value;
    }

    try {
        await api('/' + type + (id ? '/' + id : ''), {
            method: id ? 'PUT' : 'POST',
            body: JSON.stringify(payload)
        });
        closeModal();
        toast(id ? 'Alterações salvas com sucesso.' : 'Cadastro realizado com sucesso.');
        await refresh();
    } catch (error) {
        toast(error.message);
    }
};

async function removeItem(type, id) {
    if (preferences.confirmDelete && !confirm('Deseja realmente excluir este registro?')) return;
    try {
        await api('/' + type + '/' + id, { method: 'DELETE' });
        toast('Registro excluído com sucesso.');
        await refresh();
    } catch (error) {
        toast(error.message);
    }
}

async function refresh() {
    try {
        await loadAll();
        await dashboard();
        toast('Dados atualizados.');
    } catch (error) {
        toast(error.message);
    }
}

function initials(name) {
    const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return 'J';
    return parts.slice(0, 2).map(part => part[0].toUpperCase()).join('');
}

function resolveTheme(theme) {
    if (theme === 'sistema') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'escuro' : 'claro';
    }
    return theme === 'escuro' ? 'escuro' : 'claro';
}

function metaLine(role, school, year) {
    const parts = [];
    if (role) parts.push(role);
    if (school) parts.push(school);
    if (year) parts.push('Ano letivo ' + year);
    return parts.join(' · ');
}

function sanitizeSettings(saved) {
    const next = { ...SETTINGS_DEFAULTS };
    if (typeof saved.name === 'string' && saved.name.trim()) next.name = saved.name.trim();
    if (ROLES.includes(saved.role)) next.role = saved.role;
    if (typeof saved.message === 'string') next.message = saved.message.trim();
    if (typeof saved.school === 'string') next.school = saved.school.trim();
    if (typeof saved.year === 'string' && /^\d{4}$/.test(saved.year)) {
        const year = Number(saved.year);
        if (year >= 2000 && year <= 2100) next.year = saved.year;
    }
    if (saved.theme === 'claro' || saved.theme === 'escuro' || saved.theme === 'sistema') next.theme = saved.theme;
    if (saved.density === 'confortavel' || saved.density === 'compacta') next.density = saved.density;
    if (typeof saved.confirmDelete === 'boolean') next.confirmDelete = saved.confirmDelete;
    if (typeof saved.showClassCards === 'boolean') next.showClassCards = saved.showClassCards;
    const limit = Number(saved.previewLimit);
    if (Number.isFinite(limit)) next.previewLimit = Math.min(6, Math.max(1, Math.round(limit)));
    return next;
}

function updateSettingsPreview() {
    const name = document.querySelector('#display-name').value.trim() || preferences.name || SETTINGS_DEFAULTS.name;
    const role = document.querySelector('#display-role').value || preferences.role;
    const message = document.querySelector('#welcome-message').value.trim() || SETTINGS_DEFAULTS.message;
    const school = document.querySelector('#school-name').value.trim();
    const year = document.querySelector('#school-year-input').value.trim() || preferences.year;
    document.querySelector('#preview-avatar').textContent = initials(name);
    document.querySelector('#preview-title').textContent = `Olá, ${name}!`;
    document.querySelector('#preview-role').textContent = role;
    document.querySelector('#preview-message').textContent = message;
    document.querySelector('#preview-meta').textContent = metaLine(role, school, year);
}

function fillSettingsForm() {
    document.querySelector('#display-name').value = preferences.name;
    document.querySelector('#display-role').value = preferences.role;
    document.querySelector('#welcome-message').value = preferences.message;
    document.querySelector('#school-name').value = preferences.school;
    document.querySelector('#school-year-input').value = preferences.year;
    document.querySelector('#theme-mode').value = preferences.theme;
    document.querySelector('#density-mode').value = preferences.density;
    document.querySelector('#confirm-delete').value = preferences.confirmDelete ? 'sim' : 'nao';
    document.querySelector('#preview-limit').value = String(preferences.previewLimit);
    document.querySelector('#show-class-cards').value = preferences.showClassCards ? 'sim' : 'nao';
    updateSettingsPreview();
}

function readSettingsForm() {
    const year = document.querySelector('#school-year-input').value.trim();
    if (!/^\d{4}$/.test(year) || Number(year) < 2000 || Number(year) > 2100) {
        toast('Informe um ano letivo entre 2000 e 2100.');
        return null;
    }
    const limit = Number(document.querySelector('#preview-limit').value);
    if (!Number.isFinite(limit) || limit < 1 || limit > 6) {
        toast('A prévia do início aceita de 1 a 6 itens.');
        return null;
    }
    return sanitizeSettings({
        name: document.querySelector('#display-name').value,
        role: document.querySelector('#display-role').value,
        message: document.querySelector('#welcome-message').value,
        school: document.querySelector('#school-name').value,
        year,
        theme: document.querySelector('#theme-mode').value,
        density: document.querySelector('#density-mode').value,
        confirmDelete: document.querySelector('#confirm-delete').value === 'sim',
        previewLimit: limit,
        showClassCards: document.querySelector('#show-class-cards').value === 'sim'
    });
}

function applySettings() {
    const name = preferences.name || SETTINGS_DEFAULTS.name;
    document.querySelector('#title').textContent = `Olá, ${name}!`;
    document.querySelector('#subtitle').textContent = preferences.message || SETTINGS_DEFAULTS.message;
    const initial = initials(name);
    document.querySelector('#top-avatar').textContent = initial;
    document.querySelector('#profile-initial').textContent = initial;
    document.querySelector('#profile-name').textContent = name;
    document.querySelector('#profile-role').textContent = preferences.role;
    document.querySelector('#school-chip').textContent = metaLine(preferences.role, preferences.school, preferences.year);
    document.documentElement.dataset.tema = resolveTheme(preferences.theme);
    if (preferences.density === 'compacta') document.documentElement.dataset.density = 'compacta';
    else delete document.documentElement.dataset.density;
    updateSettingsPreview();
}

function persistPreferences() {
    localStorage.setItem('maisAulaSettings', JSON.stringify(preferences));
    applySettings();
    if (!state.ready) return;
    renderDashboard();
    renderClassCards();
}

function loadSettings() {
    let saved = {};
    try {
        saved = JSON.parse(localStorage.getItem('maisAulaSettings') || '{}');
    } catch (_) {
        saved = {};
    }
    preferences = sanitizeSettings(saved && typeof saved === 'object' ? saved : {});
    fillSettingsForm();
    applySettings();
}

function bindSettings() {
    const form = document.querySelector('#settings-form');
    form.addEventListener('input', updateSettingsPreview);
    form.addEventListener('change', updateSettingsPreview);
    form.addEventListener('submit', event => {
        event.preventDefault();
        const next = readSettingsForm();
        if (!next) return;
        preferences = next;
        persistPreferences();
        toast('Configurações salvas neste navegador.');
    });
    document.querySelector('#reset-settings').addEventListener('click', () => {
        if (!confirm('Restaurar as configurações padrão?')) return;
        preferences = { ...SETTINGS_DEFAULTS };
        fillSettingsForm();
        persistPreferences();
        toast('Configurações padrão restauradas.');
    });
}

function senhaValida(senha) {
    return senha.length >= 8 && senha.length <= 100;
}

function bindAuth() {
    document.querySelector('#login-form').addEventListener('submit', async event => {
        event.preventDefault();
        const email = document.querySelector('#login-email').value.trim().toLowerCase();
        const senha = document.querySelector('#login-senha').value;
        const button = event.submitter;
        if (!email || !senha) {
            toast('Informe e-mail e senha.');
            return;
        }
        if (button) button.disabled = true;
        try {
            const data = await api('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, senha })
            });
            localStorage.setItem(TOKEN_KEY, data.token);
            event.target.reset();
            await entrarNoApp(data.usuario);
            toast('Login realizado.');
        } catch (error) {
            toast(error.message);
        } finally {
            if (button) button.disabled = false;
        }
    });

    document.querySelector('#register-form').addEventListener('submit', async event => {
        event.preventDefault();
        const nome = document.querySelector('#reg-nome').value.trim();
        const email = document.querySelector('#reg-email').value.trim().toLowerCase();
        const senha = document.querySelector('#reg-senha').value;
        const confirma = document.querySelector('#reg-senha2').value;
        const button = event.submitter;
        if (nome.length < 3 || nome.length > 100) {
            toast('Informe um nome entre 3 e 100 caracteres.');
            return;
        }
        if (email.length > 100 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            toast('Informe um e-mail válido.');
            return;
        }
        if (!senhaValida(senha)) {
            toast('A senha precisa ter de 8 a 100 caracteres.');
            return;
        }
        if (senha !== confirma) {
            toast('As senhas não conferem.');
            return;
        }
        if (button) button.disabled = true;
        try {
            const data = await api('/auth/cadastro', {
                method: 'POST',
                body: JSON.stringify({ nome, email, senha })
            });
            localStorage.setItem(TOKEN_KEY, data.token);
            event.target.reset();
            await entrarNoApp(data.usuario);
            toast('Conta criada. Bem-vindo ao +Aula.');
        } catch (error) {
            toast(error.message);
        } finally {
            if (button) button.disabled = false;
        }
    });
}

async function bootstrap() {
    if (!localStorage.getItem(TOKEN_KEY)) {
        encerrarSessaoLocal();
        return;
    }
    try {
        const usuario = await api('/auth/me');
        await entrarNoApp(usuario);
    } catch (error) {
        if (!localStorage.getItem(TOKEN_KEY)) return;
        toast(error.message);
    }
}

document.querySelector('#refresh-button').onclick = refresh;
document.querySelector('#print-report').onclick = () => window.print();
document.querySelector('#exit-button').onclick = async () => {
    closeModal();
    try {
        await api('/auth/logout', { method: 'POST' });
    } catch (_) {}
    encerrarSessaoLocal();
    toast('Sessão encerrada.');
};

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (preferences.theme === 'sistema') applySettings();
});

bindDashboardLinks();
bindFilters();
bindSettings();
bindAuth();
loadSettings();
bootstrap();
