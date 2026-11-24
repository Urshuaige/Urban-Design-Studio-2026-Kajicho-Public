import {renderLive} from './workbench.js?v=20261120-asuka';

const copy = {
  title:['Edit and recalculate','条件を編集して再計算','编辑并重算'],
  signin:['Sign in with ChatGPT to edit','ChatGPT でログインして編集','用 ChatGPT 登录后编辑'],
  run:['Run on mdx1','mdx1 で再計算','在 mdx1 上重算'],
  progress:['Calculation progress','計算の進捗','计算进度'],
  public:['View the presets or a shared result.','プリセットと共有結果を閲覧できます。','可直接查看预设方案和已分享的结果。'],
  edit:['Choose measures and change assumptions for the same pilot area.','同じ試験範囲の対策と前提を設定します。','在同一试区选择措施并修改参数。'],
  offline:['The runner is reconnecting. Jobs can wait in the queue.','計算ホストに再接続しています。ジョブは待ち行列に残ります。','后台正在重连，提交的任务可在队列中等待。'],
  unavailable:['Live calculations are temporarily unavailable.','再計算は現在利用できません。','在线重算暂不可用。'],
  unavailableJob:['This result requires a shared link or the submitting account.','共有リンクまたは提出したアカウントが必要です。','请打开已分享的结果链接，或登录提交任务的账号。'],
  retry:['Connection interrupted. Checking this job again.','通信が途切れました。再度進捗を取得します。','连接中断，正在重新读取任务状态。'],
  invalid:['Check the parameter values and try again.','入力値を確認して再試行してください。','请核对参数后重新提交。'],
  submitError:['The request could not be confirmed. Try again with the same values.','送信結果を確認できません。同じ設定で再試行してください。','提交结果尚未确认，可用相同参数重试。'],
  shareError:['Sharing failed. Try again.','共有に失敗しました。再試行してください。','分享失败，请重试。'],
  queued:['Queued for mdx1','mdx1 の待ち行列','等待 mdx1 领取'],
  running:['Calculating on mdx1','mdx1 で計算中','mdx1 正在计算'],
  completed:['Calculation complete','計算完了','计算完成'],
  failed:['Calculation stopped. The model log is saved on mdx1.','計算停止。mdx1 にログを保存しました。','计算停止，模型日志已保存于 mdx1。'],
  inputs:['Checking inputs','入力確認','核对输入'],
  roof:['Roof calculation','屋根の計算','屋顶计算'],
  traffic:['Traffic calculation','交通の計算','交通计算'],
  shade:['Shade calculation','日陰の計算','遮阴计算'],
  assembling:['Preparing results','結果の整理','整理结果'],
  show:['Show result','結果を表示','查看结果'],
  share:['Share this result','この結果を公開','分享这次结果'],
  open:['Open shareable result','共有結果を開く','打开公开结果链接'],
  solarGroup:['Roof','屋根','屋顶'],
  streetGroup:['Curb and school','道路端と学校','路缘与校舍'],
  treeGroup:['Trial tree','試験樹木','试验树'],
  roofToggle:['Apply roof renewal','屋根更新を試す','应用屋顶更新'],
  curb:['Add cycle and planting strip','自転車道・植栽帯を追加','增设骑行与植栽带'],
  tree:['Add the trial tree','試験樹木を追加','加入试验树'],
  school:['Check school opening','学校の開放を検討','核查校舍开放'],
  loading:['Keep loading on the same side','同じ側の荷さばきを維持','保留同侧装卸'],
  sunMultiplier:['Direct-sun share factor','直達日射率の倍率','直射日照比例倍率'],
  vehiclesPerHour:['Offered vehicles per hour','時間あたりの投入台数','每小时输入车辆数'],
  treeHeightM:['Tree height (m)','樹高 (m)','树高（米）'],
  crownWidthM:['Crown width (m)','樹冠幅 (m)','冠幅（米）'],
  noAction:['Reference actions','参照措置','参考措施'],
};

const panel = document.querySelector('#workbench-edit');
const find = selector => panel.querySelector(selector);
const form = find('[data-live-form]');
const progress = find('[data-live-progress]');
const status = find('[data-live-status]');
const actions = find('[data-live-actions]');
const notice = find('[data-live-notice]');
const sign = find('[data-live-signin]');
const submitButton = form.querySelector('button[type=submit]');
const root = document.documentElement;
let session, job, pending, noticeKey;
let timer = 0, shownResult = null, loadedId = null;
const message = key => copy[key][root.lang.startsWith('ja') ? 1 : root.lang.startsWith('zh') ? 2 : 0];
const make = (tag, text) => {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  return node;
};

function translate() {
  for (const node of panel.querySelectorAll('[data-live-copy]')) node.textContent = message(node.dataset.liveCopy);
  if (noticeKey) notice.textContent = message(noticeKey);
  if (job) show(job, false);
}

function setNotice(key) {
  noticeKey = key;
  notice.textContent = message(key);
}

async function request(path, data) {
  const res = await fetch('/api/workbench'+path, data === undefined
    ? {cache:'no-store'}
    : {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
  if (!res.ok) {
    const error = new Error('Workbench returned HTTP '+res.status);
    error.status = res.status;
    throw error;
  }
  return res.json();
}

function field(title, controls) {
  const box = make('fieldset');
  const legend = make('legend');
  legend.dataset.liveCopy = title;
  box.append(legend);
  for (const key of controls) {
    const parameter = session.contract.parameters[key];
    const label = make('label');
    label.className = 'wb-option';
    const input = make('input');
    input.name = key;
    const name = make('span');
    name.dataset.liveCopy = key === 'roof' ? 'roofToggle' : key;
    if (parameter) {
      input.type = 'number';
      input.required = true;
      input.value = parameter.default;
      input.min = parameter.min;
      input.max = parameter.max;
      input.step = parameter.step;
      label.append(name, input);
    } else {
      input.type = 'checkbox';
      input.checked = session.contract.measures[key];
      label.append(input, ' ', name);
    }
    box.append(label);
  }
  return box;
}

function mountForm() {
  find('[data-live-fields]').append(
    field('solarGroup',['roof','sunMultiplier']),
    field('streetGroup',['curb','loading','school','vehiclesPerHour']),
    field('treeGroup',['tree','treeHeightM','crownWidthM']),
  );
  form.hidden = false;
}

function jobURL(id) {
  const url = new URL('/scenario-workbench', location.origin);
  url.searchParams.set('job', id);
  return url;
}

function action(key, click) {
  const b = make('button',message(key));
  b.type = 'button';
  b.addEventListener('click',click);
  return b;
}

function show(item, reveal = true) {
  job = item;
  find('[data-live-job]').hidden = false;
  progress.max = item.steps;
  progress.value = item.finished;
  status.textContent = message(item.state) + (item.state === 'running' && copy[item.phase] ? ' · ' + message(item.phase) : '');
  const enabled = ['roof','curb','tree','school','loading'].filter(key => item.inputs[key]);
  const parts = enabled.map(key=>message(key === 'roof' ? 'roofToggle' : key));
  if (!parts.length) parts.push(message('noAction'));
  for (const key of ['sunMultiplier','vehiclesPerHour','treeHeightM','crownWidthM']) {
    if ((key === 'sunMultiplier' && !item.inputs.roof) ||
        (['treeHeightM','crownWidthM'].includes(key) && !item.inputs.tree)) continue;
    parts.push(message(key) + ' ' + item.inputs[key]);
  }
  find('[data-live-parameters]').textContent = parts.join(' · ');
  if (item.id !== loadedId) {
    for (const input of form.querySelectorAll('input')) {
      if (input.type === 'checkbox') input.checked = item.inputs[input.name];
      else input.value = item.inputs[input.name];
    }
    loadedId = item.id;
  }
  actions.replaceChildren();
  if (item.state !== 'completed' || !item.result) return;
  if (reveal && shownResult !== item.id) {
    renderLive(item.result);
    shownResult = item.id;
  }
  actions.append(action('show', () => {
    renderLive(item.result);
    document.querySelector('#workbench-results').scrollIntoView({block:'start'});
  }));
  if (item.shared) {
    const link = make('a',message('open'));
    link.href = jobURL(item.id).href;
    actions.append(link);
  } else if (item.editable) {
    actions.append(action('share', async event => {
      const button = event.currentTarget;
      button.disabled = true;
      try { show(await request('/jobs/'+item.id+'/share', {})); }
      catch { setNotice('shareError'); button.disabled = false; }
    }));
  }
}

function checkAgain(id, elapsed = 1500) {
  clearTimeout(timer);
  timer = setTimeout(() => watch(id),elapsed);
}

async function watch(id) {
  try {
    const item = await request('/jobs/'+id);
    if (tracked !== id) return;
    if (noticeKey === 'retry') setNotice(session?.editor ? 'edit' : 'public');
    show(item);
    if (item.state === 'queued' || item.state === 'running') checkAgain(id);
  } catch (error) {
    if (tracked !== id) return;
    if (error.status === 404) setNotice('unavailableJob');
    else { setNotice('retry'); checkAgain(id,3500); }
  }
}

let tracked = new URLSearchParams(location.search).get('job');
form.addEventListener('submit',async event => {
  event.preventDefault();
  if (!form.reportValidity() || submitButton.disabled) return;
  submitButton.disabled = true;
  const inputs = {};
  for (const input of form.querySelectorAll('input')) {
    inputs[input.name] = input.type === 'checkbox' ? input.checked : input.valueAsNumber;
  }
  const serialized = JSON.stringify(inputs);
  if (!pending || pending.serialized !== serialized) pending = {serialized, id:crypto.randomUUID()};
  try {
    const item = await request('/jobs',{requestId:pending.id,foundation:session.contract.foundation,inputs});
    pending = null;
    tracked = item.id;
    history.replaceState(null,'',jobURL(item.id).href);
    show(item);
    checkAgain(item.id);
  } catch (error) {
    setNotice(error.status === 422 ? 'invalid' : 'submitError');
  } finally { submitButton.disabled = false; }
});

addEventListener('pagehide', () => clearTimeout(timer));
new MutationObserver(translate).observe(root,{attributes:true,attributeFilter:['lang']});
try {
  session = await request('/session');
  if (session.editor) {
    mountForm();
    setNotice(session.workerReady ? 'edit' : 'offline');
  } else {
    sign.hidden = session.signedIn;
    const back = location.pathname + location.search + '#workbench-edit';
    sign.href = '/signin-with-chatgpt?return_to=' + encodeURIComponent(back);
    setNotice('public');
  }
  if (tracked && /^[a-f0-9-]{36}$/.test(tracked)) await watch(tracked);
  translate();
} catch {
  setNotice('unavailable');
  translate();
}
