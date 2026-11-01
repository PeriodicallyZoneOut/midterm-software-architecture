const $ = selector => document.querySelector(selector);
let state, events = [], selected = null, loading = false, mqLoading = false, lastPublished = -1;
const labels = {listening:'Đang lắng nghe',processing:'Đang xử lý',retry:'Đang thử lại', 'awaiting-smtp':'Chờ cấu hình SMTP',connecting:'Đang kết nối'};
function rows(target, values) { const row=document.createElement('tr'); for(const value of values){const td=document.createElement('td');td.textContent=value ?? '—';row.append(td);}$(target).append(row); }
function renderEvent(){
  const event=events.find(e=>e.eventId===$('#event-select').value);
  $('#source-json').textContent=event?JSON.stringify(event,null,2):'Chưa có event trên MQ.';
  $('#event-meta').textContent=event?`MQ offset #${event.brokerOffset} · ${event.eventId} · ${event.notifyEmail===false?'Nhập lịch sử — không gửi thư':'Gửi đến cả hai consumer'}`:'';
  const d=event?.data;
  $('#target-json').textContent=d?JSON.stringify({person_id:d.id,full_name:d.fullName,email:d.email??null,dob:d.dob,version:d.version,deleted:d.operation==='deleted',recorded_at:d.recordedAt,source_event_id:event.eventId},null,2):'Chưa có dữ liệu.';
}
function renderEmail(){
  const delivery=state?.email.deliveries.find(e=>e.event_id===$('#email-select').value);
  if(!delivery){$('#email-preview').textContent='Chưa có thư.';return;}
  const event=typeof delivery.payload_json==='string'?JSON.parse(delivery.payload_json):delivery.payload_json;
  $('#email-preview').textContent=JSON.stringify({to:delivery.recipient,eventId:delivery.event_id,status:delivery.status,smtpMessageId:delivery.message_id,sentAt:delivery.sent_at,profile:event.data},null,2);
}
function render(){
  const {source,adapter,target,email}=state;
  $('#sync-state').textContent=source.error?'MQ chưa kết nối':adapter.lag?'Read DB đang đồng bộ':'Read DB đã đồng bộ';
  $('#outbox-count').textContent=source.outbox.total+' / '+source.outbox.unpublished;
  $('#retained-count').textContent=source.queues[0]?.retained??'—';
  $('#read-pending').textContent=adapter.lag;$('#email-pending').textContent=email.pending;
  for(const [name,prefix] of [['read-db','read'],['email','email']]){
    const worker=state.consumers.find(w=>w.name===name);
    $('#'+prefix+'-state').textContent=worker?.alive?(labels[worker.state]||worker.state):'Worker chưa hoạt động';
    $('#'+prefix+'-offset').textContent=`Offset riêng: ${worker?.broker_offset??-1} · Event cuối: ${worker?.last_event_id||'chưa có'}`;
    $('#'+prefix+'-error').textContent=worker?.last_error||'';
    if(name==='email')$('#smtp-state').textContent=worker?.detail?.smtpConfigured?'Đã nhập tài khoản SMTP':'Chưa nhập SMTP_USER / SMTP_PASS trong .env.smtp';
  }
  const publisher=state.consumers.find(w=>w.name==='publisher');
  $('#publisher-state').textContent=`Publisher: ${publisher?.state||'đang kết nối'} · ${publisher?.last_error||'Đã bật publisher confirms'} · Người gửi và người nhận có thể cùng Gmail.`;
  $('#flow-error').textContent=source.error||'';$('#flow-error').hidden=!source.error;
  $('#read-rows').replaceChildren();
  for(const person of target.people)rows('#read-rows',[person.full_name,person.email||'Chưa có',person.version,person.dob,person.deleted?'Đã xóa':'Đang hiển thị']);
  $('#read-empty').hidden=target.people.length>0;
  $('#email-rows').replaceChildren();
  const mailLabels={sent:'SMTP chấp nhận',sending:'Đang gửi',retry:'Chờ thử lại',pending:'Đang chờ','awaiting-config':'Chờ SMTP','skipped-history':'Nhập lịch sử — không gửi'};
  const selectedMail=$('#email-select').value;$('#email-select').replaceChildren();
  for(const item of email.deliveries){rows('#email-rows',[item.event_id.slice(0,8),item.recipient,mailLabels[item.status]||item.status,item.attempts,item.last_error||item.sent_at||'—']);const option=document.createElement('option');option.value=item.event_id;option.textContent=`${item.event_id.slice(0,8)} · ${mailLabels[item.status]||item.status}`;$('#email-select').append(option);}
  if(email.deliveries.some(e=>e.event_id===selectedMail))$('#email-select').value=selectedMail;
  renderEmail();$('#email-empty').hidden=email.deliveries.length>0;
  $('#flow-updated').textContent='Cập nhật '+new Date().toLocaleTimeString('vi-VN')+' · 2 consumer nghiệp vụ; trình xem MQ tạo một reader tạm thời khi đọc.';
}
async function loadMQ(){
  if(mqLoading)return;mqLoading=true;
  try{const response=await fetch('/api/mq/events');const body=await response.json();if(!response.ok)throw Error(body.error);events=body.events;$('#event-select').replaceChildren();for(const event of events){const o=document.createElement('option');o.value=event.eventId;o.textContent=`Offset #${event.brokerOffset} · ${event.eventType} · ${event.data.fullName}`;$('#event-select').append(o);}if(events.some(e=>e.eventId===selected))$('#event-select').value=selected;renderEvent();$('#mq-note').textContent=`Đã đọc ${events.length} event giữ lại trên stream. ACK của trình xem không xóa event.`;}
  catch(error){$('#mq-note').textContent='Chưa đọc được MQ: '+error.message;}finally{mqLoading=false;}
}
async function refresh(){
  if(loading)return;loading=true;
  try{const response=await fetch('/api/projection');const body=await response.json();if(!response.ok)throw Error(body.error);state=body;render();const published=state.source.outbox.total-state.source.outbox.unpublished;if(published!==lastPublished){lastPublished=published;await loadMQ();}}
  catch(error){$('#flow-error').textContent=error.message;$('#flow-error').hidden=false;}finally{loading=false;}
}
$('#flow-refresh').addEventListener('click',()=>{lastPublished=-1;refresh();});$('#mq-read').addEventListener('click',loadMQ);$('#event-select').addEventListener('change',()=>{selected=$('#event-select').value;renderEvent();});$('#email-select').addEventListener('change',renderEmail);setInterval(()=>{if(!document.hidden)refresh();},2000);refresh();
