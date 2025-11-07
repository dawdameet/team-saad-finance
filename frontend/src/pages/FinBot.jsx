import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function FinBot({ onToast }){
  const [q, setQ] = useState('')
  const [chat, setChat] = useState([])
  const [loading, setLoading] = useState(false)
  const suggestions = [
    'How can I optimize my tax under the old regime?',
    'Create a monthly budget for ₹80,000 income',
    'Should I prepay my loan or invest instead?',
    'What’s a good SIP amount for 12% CAGR?'
  ]

  async function ask(){
    if(!q.trim() || loading) return
    setLoading(true)
    try{
      const timestamp = new Date().toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'})
      const prompt = q
      setChat(prev => [...prev, {role:'user', text:prompt, time:timestamp}])
      setQ('')
      const r = await api('/api/finbot/chat', { method:'POST', body: { message: prompt }})
      setChat(prev => [...prev, {role:'bot', text:r.reply, time:timestamp}])
    }catch(e){ onToast?.(e.message) }
    finally{ setLoading(false) }
  }

  function onKeyDown(e){
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault(); ask();
    }
  }

  function copyText(text){
    try{ navigator.clipboard.writeText(text); onToast?.('Copied') }catch(_){/* ignore */}
  }

  return (
    <div className="card" style={{padding:'0'}}>
      <div style={{display:'flex',alignItems:'center',gap:10,padding:'12px 16px',borderBottom:'1px solid rgba(165,180,252,0.2)'}}>
        <div style={{width:36,height:36,borderRadius:10,display:'flex',alignItems:'center',justifyContent:'center',background:'linear-gradient(135deg,#8B5CF6,#6366F1)'}}>🤖</div>
        <div style={{display:'flex',flexDirection:'column'}}>
          <div style={{fontWeight:700}}>FinBot</div>
          <div className="small" style={{opacity:0.8}}>Your AI finance assistant</div>
        </div>
      </div>

      <div style={{padding:'12px 16px',borderBottom:'1px solid rgba(165,180,252,0.1)'}}>
        <div className="small" style={{opacity:0.9, marginBottom:8}}>Try a quick question</div>
        <div style={{display:'flex',flexWrap:'wrap',gap:8}}>
          {suggestions.map((s,i)=>(
            <button key={i} className="btn btn-ghost" onClick={()=>setQ(s)}>{s}</button>
          ))}
        </div>
      </div>

      <div style={{maxHeight:420,overflowY:'auto',padding:'12px 16px'}}>
        {chat.length === 0 && (
          <div style={{padding:'12px',border:'1px dashed rgba(165,180,252,0.4)',borderRadius:10,marginBottom:12}}>
            Ask anything about taxes, budgeting, investments, or credit. Use the suggestions above to get started.
          </div>
        )}
        {chat.map((m,i)=>(
          <div key={i} style={{display:'flex',gap:'10px',marginBottom:14,alignItems:'flex-start'}}>
            <div style={{width:32,height:32,borderRadius:'50%',background:m.role==='bot'?'#8B5CF6':'#2a2750',display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0,fontSize:16}}>
              {m.role==='bot'?'🤖':'👤'}
            </div>
            <div style={{flex:1}}>
              <div style={{background:m.role==='bot'?'rgba(139,92,246,0.12)':'rgba(165,180,252,0.12)',padding:'12px 14px',borderRadius:12,position:'relative'}}>
                <div>{m.text}</div>
                {m.role==='bot' && (
                  <button onClick={()=>copyText(m.text)} className="btn btn-ghost" style={{position:'absolute',right:6,top:6,fontSize:12,padding:'2px 6px'}}>Copy</button>
                )}
              </div>
              <div className="small" style={{opacity:0.7, marginTop:4}}>{m.time}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{display:'flex',gap:10,alignItems:'center',opacity:0.9}}>
            <div style={{width:10,height:10,borderRadius:'50%',background:'#A5B4FC',animation:'pulse 1s infinite alternate'}}></div>
            <div className="small">FinBot is typing…</div>
          </div>
        )}
      </div>

      <div style={{padding:'12px 16px',borderTop:'1px solid rgba(165,180,252,0.2)'}}>
        <div style={{position:'relative'}}>
          <textarea 
            className="textarea"
            rows="3"
            value={q}
            onChange={e=>setQ(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask about taxes, budgets, investments… (Press Enter to send, Shift+Enter for newline)"
            style={{paddingRight:60}}
            aria-label="Ask FinBot a question"
          />
          <button 
            onClick={ask}
            aria-label="Send message"
            disabled={!q.trim() || loading}
            style={{
              position:'absolute', right:12, bottom:12, width:40, height:40, borderRadius:'50%',
              background: loading? 'rgba(226,232,240,0.6)' : '#E2E8F0', border:'none', cursor:(!q.trim()||loading)?'not-allowed':'pointer',
              display:'flex', alignItems:'center', justifyContent:'center', fontSize:20, color:'#1E1B3A', transition:'all 0.2s'
            }}
          >↑</button>
        </div>
      </div>
    </div>
  )
}
