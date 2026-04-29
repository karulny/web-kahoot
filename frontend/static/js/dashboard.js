let questionCount = 0;

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
        <button class="btn btn-ghost btn-sm" onclick="deleteQuiz(${q.id})">Удалить</button>
      </div>
    </div>
  `).join('');
}

function ending(n) {
  if (n % 10 === 1 && n % 100 !== 11) return '';
  if ([2,3,4].includes(n % 10) && ![12,13,14].includes(n % 100)) return 'а';
  return 'ов';
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', {day: 'numeric', month: 'short'});
}

async function startGame(quizId, pin) {
  const res = await authFetch(`/game/start/${quizId}`, {method: 'POST'});
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
  const res = await authFetch(`/quiz/${id}`, {method: 'DELETE'});
  const data = await res.json();
  if (data.success) loadQuizzes();
  else alert(data.message);
}

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
  el.innerHTML = `
    <div class="qb-header">
      <span class="qb-num">Вопрос ${id}</span>
      <button class="btn-remove" onclick="removeQuestion(${id})">✕</button>
    </div>
    <div class="field">
      <input type="text" placeholder="Текст вопроса" class="qb-text">
    </div>
    <div class="field">
      <select class="qb-type">
        <option value="single">Один вариант</option>
        <option value="multiple">Несколько вариантов</option>
        <option value="poll">Голосование (без правильного)</option>
      </select>
    </div>
    <div class="qb-answers" id="qa-${id}">
      ${makeAnswerRow(id, 1)}
      ${makeAnswerRow(id, 2)}
    </div>
    <button class="btn btn-ghost btn-sm" onclick="addAnswer(${id})">+ Вариант</button>
  `;
  document.getElementById('questions-list').appendChild(el);
}

function makeAnswerRow(qid, aid) {
  return `<div class="answer-row" id="ar-${qid}-${aid}">
    <input type="checkbox" class="ans-correct" title="Правильный">
    <input type="text" class="ans-text" placeholder="Вариант ответа">
    <button class="btn-remove-sm" onclick="removeAnswer('${qid}','${aid}')">✕</button>
  </div>`;
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

async function saveQuiz() {
  const title = document.getElementById('quiz-title').value.trim();
  const err = document.getElementById('create-error');
  err.textContent = '';

  if (!title) { err.textContent = 'Введи название'; return; }

  const qBuilders = document.querySelectorAll('.question-builder');
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
      if (t) answers.push({text: t, is_correct: correct});
    }

    if (answers.length < 2) { err.textContent = 'Минимум 2 варианта в каждом вопросе'; return; }
    if (type !== 'poll' && !answers.some(a => a.is_correct)) {
      err.textContent = 'Отметь правильный ответ (или выбери "Голосование")'; return;
    }

    questions.push({text, question_type: type, answers});
  }

  const res = await authFetch('/quiz/', {
    method: 'POST',
    body: JSON.stringify({title, questions})
  });
  const data = await res.json();
  if (data.success) {
    hideCreateModal();
    loadQuizzes();
  } else {
    err.textContent = data.message;
  }
}

function copyPin(pin) {
  navigator.clipboard.writeText(pin).then(() => {
    alert(`PIN ${pin} скопирован!`);
  });
}

loadQuizzes();