let questionCount = 0;
let editQuestionCount = 0;

function authFetch(url, options = {}) {
  const token = localStorage.getItem('token');
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token,
      ...(options.headers || {})
    }
  });
}

/* ── QUIZ LIST ── */

async function loadQuizzes() {
  const res = await authFetch('/quiz/');
  const data = await res.json();
  const list = document.getElementById('quiz-list');
  const countEl = document.getElementById('quiz-count');

  if (!data.success || !data.quizzes.length) {
    list.innerHTML = `<div class="empty-state">
      <div class="empty-icon">📝</div>
      <p>У тебя пока нет квизов</p>
      <button class="btn btn-primary" onclick="showCreateModal()">Создать первый</button>
    </div>`;
    countEl.textContent = 'Нет квизов';
    return;
  }

  countEl.textContent = `${data.quizzes.length} квиз${ending(data.quizzes.length)}`;
  list.innerHTML = data.quizzes.map(q => `
    <div class="quiz-card" data-id="${q.id}">
      <div class="quiz-card-header">
        <span class="quiz-pin">PIN: ${q.pin}</span>
        <span class="quiz-date">${formatDate(q.date)}</span>
      </div>
      <h3 class="quiz-title">${q.title}</h3>
      <p class="quiz-meta">${q.count} вопрос${ending(q.count)}</p>
      <div class="quiz-actions">
        <button class="btn btn-primary btn-sm" onclick="startGame(${q.id}, '${q.pin}')">▶ Запустить</button>
        <button class="btn btn-outline btn-sm" onclick="openEditModal(${q.id})">✎ Изменить</button>
        <button class="btn btn-ghost btn-sm" onclick="deleteQuiz(${q.id})">Удалить</button>
      </div>
    </div>
  `).join('');
}

function ending(n) {
  if (n % 10 === 1 && n % 100 !== 11) return '';
  if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return 'а';
  return 'ов';
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
}

/* ── GAME ── */

async function startGame(quizId, pin) {
  const res = await authFetch(`/game/start/${quizId}`, { method: 'POST' });
  const data = await res.json();
  if (data.success) {
    location.href = `/host/${data.session_id}/${pin}`;
  } else {
    if (data.session_id) {
      location.href = `/host/${data.session_id}/${pin}`;
    } else {
      alert(data.message);
    }
  }
}

async function deleteQuiz(id) {
  if (!confirm('Удалить квиз?')) return;
  const res = await authFetch(`/quiz/${id}`, { method: 'DELETE' });
  const data = await res.json();
  if (data.success) loadQuizzes();
  else alert(data.message);
}

/* ── CREATE MODAL ── */

function showCreateModal() {
  questionCount = 0;
  document.getElementById('quiz-title').value = '';
  document.getElementById('questions-list').innerHTML = '';
  document.getElementById('create-error').textContent = '';
  document.getElementById('create-modal').classList.remove('hidden');
  addQuestion();
}

function hideCreateModal() {
  document.getElementById('create-modal').classList.add('hidden');
}

function addQuestion() {
  questionCount++;
  const id = questionCount;
  const el = document.createElement('div');
  el.className = 'question-builder';
  el.id = `q-${id}`;
  el.innerHTML = buildQuestionHTML(id, `Вопрос ${id}`);
  document.getElementById('questions-list').appendChild(el);
}

function makeAnswerRow(qid, aid, text = '', correct = false) {
  return `<div class="answer-row" id="ar-${qid}-${aid}">
    <input type="checkbox" class="ans-correct" title="Правильный" ${correct ? 'checked' : ''}>
    <input type="text" class="ans-text" placeholder="Вариант ответа" value="${escapeHtml(text)}">
    <button class="btn-remove-sm" onclick="removeAnswer('${qid}','${aid}')">✕</button>
  </div>`;
}

function buildQuestionHTML(id, label, text = '', type = 'single', answers = []) {
  const defaultAnswers = answers.length
    ? answers.map((a, i) => makeAnswerRow(id, i + 1, a.text || a, a.correct || a.is_correct || false)).join('')
    : makeAnswerRow(id, 1) + makeAnswerRow(id, 2);

  return `
    <div class="qb-header">
      <span class="qb-num">${label}</span>
      <button class="btn-remove" onclick="removeQuestion(${id})">✕</button>
    </div>
    <div class="field">
      <input type="text" placeholder="Текст вопроса" class="qb-text" value="${escapeHtml(text)}">
    </div>
    <div class="field">
      <select class="qb-type">
        <option value="single" ${type === 'single' ? 'selected' : ''}>Один вариант</option>
        <option value="multiple" ${type === 'multiple' ? 'selected' : ''}>Несколько вариантов</option>
        <option value="poll" ${type === 'poll' ? 'selected' : ''}>Голосование (без правильного)</option>
      </select>
    </div>
    <div class="qb-answers" id="qa-${id}">
      ${defaultAnswers}
    </div>
    <button class="btn btn-ghost btn-sm" onclick="addAnswer(${id})">+ Вариант</button>
  `;
}

function addAnswer(qid) {
  const container = document.getElementById(`qa-${qid}`);
  container.insertAdjacentHTML('beforeend', makeAnswerRow(qid, Date.now()));
}

function removeAnswer(qid, aid) {
  const el = document.getElementById(`ar-${qid}-${aid}`);
  if (el) el.remove();
}

function removeQuestion(id) {
  const el = document.getElementById(`q-${id}`);
  if (el) el.remove();
}

function collectQuestions(container) {
  const qBuilders = container.querySelectorAll('.question-builder');
  const questions = [];
  const err = container.closest('.modal-box')
    ? container.closest('.modal-box').querySelector('.form-error')
    : null;

  for (const qEl of qBuilders) {
    const text = qEl.querySelector('.qb-text').value.trim();
    const type = qEl.querySelector('.qb-type').value;
    if (!text) return { error: 'Заполни все вопросы' };

    const ansRows = qEl.querySelectorAll('.answer-row');
    const answers = [];
    for (const row of ansRows) {
      const t = row.querySelector('.ans-text').value.trim();
      const correct = row.querySelector('.ans-correct').checked;
      if (t) answers.push({ text: t, is_correct: correct });
    }

    if (answers.length < 2) return { error: 'Минимум 2 варианта в каждом вопросе' };
    if (type !== 'poll' && !answers.some(a => a.is_correct)) {
      return { error: 'Отметь правильный ответ (или выбери «Голосование»)' };
    }
    questions.push({ text, question_type: type, answers });
  }

  if (!questions.length) return { error: 'Добавь хотя бы один вопрос' };
  return { questions };
}

async function saveQuiz() {
  const title = document.getElementById('quiz-title').value.trim();
  const err = document.getElementById('create-error');
  err.textContent = '';

  if (!title) { err.textContent = 'Введи название'; return; }

  const { questions, error } = collectQuestions(document.getElementById('questions-list'));
  if (error) { err.textContent = error; return; }

  const res = await authFetch('/quiz/', {
    method: 'POST',
    body: JSON.stringify({ title, questions })
  });
  const data = await res.json();
  if (data.success) {
    hideCreateModal();
    loadQuizzes();
  } else {
    err.textContent = data.message;
  }
}

/* ── EDIT MODAL ── */

async function openEditModal(quizId) {
  const res = await authFetch(`/quiz/${quizId}`);
  const data = await res.json();
  if (!data.success) { alert('Не удалось загрузить квиз'); return; }

  const quiz = data.quiz;
  editQuestionCount = 0;

  document.getElementById('edit-quiz-id').value = quiz.id;
  document.getElementById('edit-quiz-title').value = quiz.title;
  document.getElementById('edit-questions-list').innerHTML = '';
  document.getElementById('edit-error').textContent = '';

  for (const q of quiz.questions) {
    editQuestionCount++;
    const id = editQuestionCount;
    const el = document.createElement('div');
    el.className = 'question-builder';
    el.id = `eq-${id}`;
    el.innerHTML = buildEditQuestionHTML(id, `Вопрос ${id}`, q.text, q.type, q.answers);
    document.getElementById('edit-questions-list').appendChild(el);
  }

  document.getElementById('edit-modal').classList.remove('hidden');
}

function buildEditQuestionHTML(id, label, text = '', type = 'single', answers = []) {
  const answersHTML = answers.length
    ? answers.map((a, i) => makeEditAnswerRow(id, i + 1, a.text, a.correct)).join('')
    : makeEditAnswerRow(id, 1) + makeEditAnswerRow(id, 2);

  return `
    <div class="qb-header">
      <span class="qb-num">${label}</span>
      <button class="btn-remove" onclick="removeEditQuestion(${id})">✕</button>
    </div>
    <div class="field">
      <input type="text" placeholder="Текст вопроса" class="qb-text" value="${escapeHtml(text)}">
    </div>
    <div class="field">
      <select class="qb-type">
        <option value="single" ${type === 'single' ? 'selected' : ''}>Один вариант</option>
        <option value="multiple" ${type === 'multiple' ? 'selected' : ''}>Несколько вариантов</option>
        <option value="poll" ${type === 'poll' ? 'selected' : ''}>Голосование (без правильного)</option>
      </select>
    </div>
    <div class="qb-answers" id="eqa-${id}">
      ${answersHTML}
    </div>
    <button class="btn btn-ghost btn-sm" onclick="addEditAnswer(${id})">+ Вариант</button>
  `;
}

function makeEditAnswerRow(qid, aid, text = '', correct = false) {
  return `<div class="answer-row" id="ear-${qid}-${aid}">
    <input type="checkbox" class="ans-correct" title="Правильный" ${correct ? 'checked' : ''}>
    <input type="text" class="ans-text" placeholder="Вариант ответа" value="${escapeHtml(text)}">
    <button class="btn-remove-sm" onclick="removeEditAnswer('${qid}','${aid}')">✕</button>
  </div>`;
}

function addEditQuestion() {
  editQuestionCount++;
  const id = editQuestionCount;
  const el = document.createElement('div');
  el.className = 'question-builder';
  el.id = `eq-${id}`;
  el.innerHTML = buildEditQuestionHTML(id, `Вопрос ${id}`);
  document.getElementById('edit-questions-list').appendChild(el);
}

function removeEditQuestion(id) {
  const el = document.getElementById(`eq-${id}`);
  if (el) el.remove();
}

function addEditAnswer(qid) {
  const container = document.getElementById(`eqa-${qid}`);
  container.insertAdjacentHTML('beforeend', makeEditAnswerRow(qid, Date.now()));
}

function removeEditAnswer(qid, aid) {
  const el = document.getElementById(`ear-${qid}-${aid}`);
  if (el) el.remove();
}

function hideEditModal() {
  document.getElementById('edit-modal').classList.add('hidden');
}

async function saveEditQuiz() {
  const quizId = document.getElementById('edit-quiz-id').value;
  const title = document.getElementById('edit-quiz-title').value.trim();
  const err = document.getElementById('edit-error');
  err.textContent = '';

  if (!title) { err.textContent = 'Введи название'; return; }

  const list = document.getElementById('edit-questions-list');
  const qBuilders = list.querySelectorAll('.question-builder');
  if (!qBuilders.length) { err.textContent = 'Добавь хотя бы один вопрос'; return; }

  const questions = [];
  for (const qEl of qBuilders) {
    const text = qEl.querySelector('.qb-text').value.trim();
    const type = qEl.querySelector('.qb-type').value;
    if (!text) { err.textContent = 'Заполни все вопросы'; return; }

    const ansRows = qEl.querySelectorAll('.answer-row');
    const answers = [];
    for (const row of ansRows) {
      const t = row.querySelector('.ans-text').value.trim();
      const correct = row.querySelector('.ans-correct').checked;
      if (t) answers.push({ text: t, is_correct: correct });
    }

    if (answers.length < 2) { err.textContent = 'Минимум 2 варианта в каждом вопросе'; return; }
    if (type !== 'poll' && !answers.some(a => a.is_correct)) {
      err.textContent = 'Отметь правильный ответ (или выбери «Голосование»)';
      return;
    }
    questions.push({ text, question_type: type, answers });
  }

  const res = await authFetch(`/quiz/${quizId}`, {
    method: 'PUT',
    body: JSON.stringify({ title, questions })
  });
  const data = await res.json();
  if (data.success) {
    hideEditModal();
    loadQuizzes();
  } else {
    err.textContent = data.message;
  }
}

/* ── UTILS ── */

function escapeHtml(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = '/';
}

/* ── INIT ── */
loadQuizzes();
