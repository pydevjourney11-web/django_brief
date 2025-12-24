(function(){
  const root=document.querySelector('[data-brief-uuid]');
  if(!root) return;
  const isCompleted=root.getAttribute('data-brief-completed')==='1';
  const saveIndicator=document.getElementById('saveIndicator');
  function getCookie(name){const value=`; ${document.cookie}`;const parts=value.split(`; ${name}=`);if(parts.length===2) return parts.pop().split(';').shift();return null;}
  const csrftoken=getCookie('csrftoken');
  (function(){const params=new URLSearchParams(window.location.search);if(params.get('submitted')==='1') openSubmittedModal();})();
  function openSubmittedModal(){const overlay=document.getElementById('submittedOverlay');const dialog=document.getElementById('submittedDialog');if(!overlay||!dialog) return;overlay.style.display='block';dialog.style.display='block';}
  function closeSubmittedModal(){const overlay=document.getElementById('submittedOverlay');const dialog=document.getElementById('submittedDialog');if(!overlay||!dialog) return;overlay.style.display='none';dialog.style.display='none';}
  (function(){const overlay=document.getElementById('submittedOverlay');const dialog=document.getElementById('submittedDialog');const closeBtn=dialog?dialog.querySelector('.submitted-close'):null;if(overlay) overlay.addEventListener('click', closeSubmittedModal);if(closeBtn) closeBtn.addEventListener('click', closeSubmittedModal);document.addEventListener('keydown',(e)=>{if(e.key==='Escape') closeSubmittedModal();});})();
  function setIndicator(text,cls){if(!saveIndicator) return;saveIndicator.classList.remove('ok','error');if(cls) saveIndicator.classList.add(cls);saveIndicator.textContent=text;}
  async function autosave(questionId,questionType,rawValue){if(isCompleted) return;setIndicator('Сохраняю...',null);const payload={question_id:questionId,question_type:questionType,value:rawValue};const resp=await fetch(root.getAttribute('data-autosave-url'),{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrftoken,},body:JSON.stringify(payload),});const data=await resp.json().catch(()=>null);if(!resp.ok){setIndicator(data&&data.error?data.error:'Ошибка сохранения','error');return;}setIndicator('Сохранено','ok');window.setTimeout(()=>setIndicator('Изменения сохраняются автоматически.',null),1200);}
  function getFieldValue(el){if(el.type==='checkbox'){const qid=el.getAttribute('data-question-id');const boxes=document.querySelectorAll('input[type="checkbox"][data-question-id="'+qid+'"]:checked');return Array.from(boxes).map((b)=>b.value);}if(el.tagName==='SELECT') return el.value;return el.value;}
  const timers=new Map();
  function scheduleSave(el){const qid=el.getAttribute('data-question-id');const qtype=el.getAttribute('data-question-type');if(!qid||!qtype) return;const key=`${qid}`;const value=getFieldValue(el);if(timers.has(key)) window.clearTimeout(timers.get(key));timers.set(key,window.setTimeout(()=>autosave(Number(qid),qtype,value),350));}
  if(!isCompleted && window.Choices){document.querySelectorAll('select[data-question-id]').forEach((sel)=>{const inst=new Choices(sel,{searchEnabled:false,itemSelectText:'',shouldSort:false,});if(sel.value) inst.setChoiceByValue(sel.value);});}
  const fields=document.querySelectorAll('[data-question-id]');
  fields.forEach((el)=>{el.addEventListener('change',()=>scheduleSave(el));el.addEventListener('input',()=>scheduleSave(el));});

  const reps=document.querySelectorAll('.competitors-repeater');
  reps.forEach((wrap)=>{
    const hidden=wrap.querySelector('.competitors-hidden');
    const rowsWrap=wrap.querySelector('.comp-rows');
    const addBtn=wrap.querySelector('.add-comp-row');
    let data=[];
    const minRows=5;
    function parseInitial(){try{const v=hidden.value;if(v){const arr=JSON.parse(v);if(Array.isArray(arr)) data=arr.map(o=>({url:String(o.url||''),comment:String(o.comment||'')}));}}catch(e){}if(!data.length){for(let i=0;i<minRows;i++){data.push({url:'',comment:''});}}}
    function sync(){hidden.value=JSON.stringify(data);hidden.dispatchEvent(new Event('input'));}
    function render(){rowsWrap.innerHTML='';data.forEach((item,idx)=>{const row=document.createElement('div');row.className='comp-row';const inp1=document.createElement('input');inp1.type='text';inp1.placeholder='https://...';inp1.value=item.url;inp1.className='comp-input';if(isCompleted) inp1.disabled=true;inp1.addEventListener('input',()=>{data[idx].url=inp1.value;sync();});const inp2=document.createElement('input');inp2.type='text';inp2.placeholder='Комментарий';inp2.value=item.comment;inp2.className='comp-input';if(isCompleted) inp2.disabled=true;inp2.addEventListener('input',()=>{data[idx].comment=inp2.value;sync();});row.appendChild(inp1);row.appendChild(inp2);rowsWrap.appendChild(row);});}
    parseInitial();render();sync();
    if(addBtn){if(isCompleted) addBtn.disabled=true;addBtn.addEventListener('click',()=>{data.push({url:'',comment:''});render();sync();});}
  });
})();
