import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine } from 'recharts'

export default function Credit({ onToast }){
  const [form, setForm] = useState({ income:600000, age:25, utilization:0.35, late_pay:0, dti:0.25 })
  const [score, setScore] = useState(null)
  const [pdSeries, setPdSeries] = useState([])
  const [simpleForm, setSimpleForm] = useState({ payment_history: 95, credit_utilization: 20, credit_age_years: 5, credit_types_count: 3, recent_inquiries_count: 1 })
  const [simpleScore, setSimpleScore] = useState(null)
  const [simpleErr, setSimpleErr] = useState('')
  const [simpleUpdatedAt, setSimpleUpdatedAt] = useState(null)
  const [simpleLoading, setSimpleLoading] = useState(false)

  const FEATURE_LABELS = {
    income: 'Annual Income',
    age: 'Age',
    utilization: 'Card Utilization',
    late_pay: 'Late Payments (12m)',
    dti: 'Debt-to-Income (DTI)'
  }

  

  function formatINR(n){
    try{
      return new Intl.NumberFormat('en-IN', { style:'currency', currency:'INR', maximumFractionDigits:0 }).format(n)
    }catch(_){
      return `₹ ${Number(n||0).toLocaleString('en-IN')}`
    }
  }

  async function runSimpleScore(){
    try{
      setSimpleLoading(true)
      setSimpleErr('')
      const res = await api('/api/credit/simple_score', { method:'POST', body: simpleForm })
      const val = Number(res?.score)
      if(Number.isFinite(val)){
        setSimpleScore(val)
        setSimpleUpdatedAt(new Date())
        try{
          localStorage.setItem('simple_credit_score', String(val))
          window.dispatchEvent(new Event('simple-credit-updated'))
        }catch(_){/* ignore */}
      }else{
        setSimpleScore(null)
        setSimpleErr('Could not parse score from server response')
      }
    }catch(e){ setSimpleErr(String(e?.message||e)); onToast?.(e.message) }
    finally{ setSimpleLoading(false) }
  }

async function runScore(){
  try{
    const s = await api('/api/credit/score', { method:'POST', body: form })
    const feats = Array.isArray(s?.shap?.features) ? s.shap.features : []
    let vals = Array.isArray(s?.shap?.values) ? s.shap.values : []
    if (vals && vals.values && Array.isArray(vals.values)) { vals = vals.values }
    if (feats.length !== vals.length) {
      vals = feats.map(()=>0)
    }
    const normalized = { ...s, shap: { features: feats, values: vals } }
    setScore(normalized)
    // BUG #9: Update PD trend graph state with new prediction
    const pd = Math.max(0, Math.min(1, Number(normalized?.prob_default || 0)))
    const point = { ts: Date.now(), pd: Number((pd * 100).toFixed(2)) }
    setPdSeries(prev => {
      const next = [...prev, point]
      return next.slice(Math.max(0, next.length - 60)) // retain last 60 entries
    })


    try{
      localStorage.setItem('credit_form', JSON.stringify(form))
      localStorage.setItem('credit_score', JSON.stringify(normalized))
      window.dispatchEvent(new Event('credit-updated'))
    }catch(_){/* ignore */}
  }catch(e){ onToast?.(e.message) }
}


  // Load saved form and score on mount, then trigger an initial score
  useEffect(()=>{
    try{
      const saved = JSON.parse(localStorage.getItem('credit_form')||'null')
      if(saved && typeof saved === 'object') setForm(prev => ({...prev, ...saved}))
    }catch(_){/* ignore */}
    // Ensure we compute at least once on mount
    runScore()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  // Auto-score with debounce when inputs change
  useEffect(()=>{
    const t = setTimeout(()=>{ runScore() }, 250)
    return ()=> clearTimeout(t)
  }, [form.income, form.age, form.utilization, form.late_pay, form.dti])

  // Simple score now runs only when you click the Calculate button.

  const pd = Number(score?.prob_default || 0)
  const pdPct = (pd * 100).toFixed(2)
  const pdCategory = pd < 0.1 ? { label:'Low', color:'#61D29A' } : pd < 0.25 ? { label:'Moderate', color:'#FBBF24' } : { label:'High', color:'#ff8b8b' }

  const trendData = pdSeries.map((d, i) => ({ idx: i + 1, pd: d.pd }))

  return (
    <div className="grid">
      <div className="col-6 card">
        <h3>Credit Factors</h3>
        <div className="grid" style={{gap:'12px'}}>
          <div className="col-6">
            <div className="stack" style={{padding:'8px',borderRadius:'6px',background:'rgba(165,180,252,0.05)'}}>
              <div className="label" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span>Annual Income (₹)</span>
                <span className="badge" style={{borderRadius:999, padding:'2px 8px'}}>{formatINR(form.income)}</span>
              </div>
              <input className="input" type="number" step="1000" min="0" value={form.income} onChange={e=>setForm({...form, income:Number(e.target.value)})} />
              <div className="small" style={{opacity:0.9}}>Higher income generally lowers default risk.</div>
            </div>
          </div>
          <div className="col-6">
            <div className="stack" style={{padding:'8px',borderRadius:'6px'}}>
              <div className="label" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span>Age (years)</span>
                <span className="badge" style={{borderRadius:999, padding:'2px 8px'}}>{form.age} yrs</span>
              </div>
              <input className="input" type="range" min="18" max="75" step="1" value={form.age} onChange={e=>setForm({...form, age:Number(e.target.value)})} />
              <div className="small" style={{opacity:0.9}}>Stable age bands can correlate with lower risk.</div>
            </div>
          </div>
          <div className="col-6">
            <div className="stack" style={{padding:'8px',borderRadius:'6px',background:'rgba(165,180,252,0.05)'}}>
              <div className="label" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span>Card Utilization</span>
                <span className="badge" style={{borderRadius:999, padding:'2px 8px'}}>{(form.utilization*100).toFixed(0)}%</span>
              </div>
              <input className="input" type="range" min="0" max="1" step="0.01" value={form.utilization} onChange={e=>setForm({...form, utilization:Number(e.target.value)})} />
              <div className="small" style={{opacity:0.9}}>Lower utilization (below ~30%) is healthier.</div>
            </div>
          </div>
          <div className="col-6">
            <div className="stack" style={{padding:'8px',borderRadius:'6px',background:'rgba(165,180,252,0.05)'}}>
              <div className="label" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span>Debt-to-Income (DTI)</span>
                <span className="badge" style={{borderRadius:999, padding:'2px 8px'}}>{(form.dti*100).toFixed(0)}%</span>
              </div>
              <input className="input" type="range" min="0" max="1" step="0.01" value={form.dti} onChange={e=>setForm({...form, dti:Number(e.target.value)})} />
              <div className="small" style={{opacity:0.9}}>Lower DTI (below ~35%) is preferred.</div>
            </div>
          </div>
          <div className="col-12">
            <div className="stack" style={{padding:'8px',borderRadius:'6px'}}>
              <div className="label" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span>Late Payments (last 12m)</span>
                <span className="badge" style={{borderRadius:999, padding:'2px 8px'}}>{form.late_pay}</span>
              </div>
              <input className="input" type="range" min="0" max="10" step="1" value={form.late_pay} onChange={e=>setForm({...form, late_pay:Number(e.target.value)})} />
              <div className="small" style={{opacity:0.9}}>More missed payments increase risk.</div>
            </div>
          </div>
          <div className="col-12" style={{marginTop:4}}>
            <button className="btn btn-primary" onClick={runScore} aria-label="Score credit risk button">Recalculate</button>
          </div>
        </div>
      </div>
      <div className="col-6 card">
        <h3>Risk Summary</h3>
        {score ? (
          <>
            <div style={{marginBottom:'16px'}}>
              <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'8px'}}>
                <div className="kpi" style={{fontSize:'18px'}}>Probability of Default</div>
                <span className="badge" style={{background:pdCategory.color, color:'#0b1021', padding:'4px 10px', borderRadius:'999px', fontWeight:700}}>{pdPct}% • {pdCategory.label}</span>
              </div>
              <div style={{width:'100%',height:'24px',background:'#1E1B3A',borderRadius:'12px',overflow:'hidden',border:'1px solid #A5B4FC'}}>
                <div style={{width:`${(score.prob_default*100).toFixed(2)}%`,height:'100%',background:'linear-gradient(to right, #A78BFA, #8B5CF6)',transition:'width 0.3s ease'}}></div>
              </div>
              <div className="small" style={{opacity:0.9, marginTop:6}}>Lower is better. Aim for Low risk by reducing utilization and DTI, and avoiding late payments.</div>
              <div style={{display:'flex',gap:8,marginTop:10,flexWrap:'wrap'}}>
                <span className="badge" style={{padding:'4px 8px',borderRadius:999,background:'rgba(97,210,154,0.12)',border:'1px solid #61D29A',color:'#E2E8F0'}}>Utilization {(form.utilization*100).toFixed(0)}%</span>
                <span className="badge" style={{padding:'4px 8px',borderRadius:999,background:'rgba(167,139,250,0.12)',border:'1px solid #A5B4FC',color:'#E2E8F0'}}>DTI {(form.dti*100).toFixed(0)}%</span>
                <span className="badge" style={{padding:'4px 8px',borderRadius:999,background:'rgba(251,191,36,0.12)',border:'1px solid #FBBF24',color:'#E2E8F0'}}>Late {form.late_pay}</span>
              </div>
            </div>
            <div style={{height:220}}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke="#A5B4FC" strokeOpacity={0.15} vertical={false} />
                  <XAxis dataKey="idx" stroke="#E2E8F0" tick={{ fill:'#E2E8F0', fontSize:12 }} tickLine={false} label={{ value:'Updates', position:'insideBottom', offset:-4, fill:'#E2E8F0', fontSize:11 }} />
                  <YAxis stroke="#E2E8F0" tick={{ fill:'#E2E8F0', fontSize:12 }} tickFormatter={(v)=>`${v}%`} width={48} />
                  <Tooltip contentStyle={{ background:'#2a2750', border:'1px solid #A5B4FC', color:'#FFFFFF' }} formatter={(val)=>[`${val}%`, 'PD']} />
                  <ReferenceLine y={10} stroke="#61D29A" strokeDasharray="4 4" />
                  <ReferenceLine y={25} stroke="#F59E0B" strokeDasharray="4 4" />
                  <Line type="monotone" dataKey="pd" stroke="#A5B4FC" strokeWidth={3} dot={false} isAnimationActive={true} animationDuration={400} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : <div className="small">Adjust the factors to see your updated risk instantly.</div>}
      </div>

      <div className="col-12 card">
        <h3>Simple Credit Score (300–850)</h3>
        <div className="grid" style={{gap:'12px'}}>
          <div className="col-6">
            <div className="stack" style={{gap:'10px'}}>
              <div className="stack" style={{padding:'8px',borderRadius:'6px',background:'rgba(165,180,252,0.05)'}}>
                <div className="label">Payment History (%)</div>
                <input className="input" type="range" min="0" max="100" step="1" value={simpleForm.payment_history} onChange={e=>setSimpleForm({...simpleForm, payment_history:Number(e.target.value)})} />
                <div className="small">{simpleForm.payment_history}% • On-time payment rate.</div>
              </div>
              <div className="stack" style={{padding:'8px',borderRadius:'6px'}}>
                <div className="label">Credit Utilization (%)</div>
                <input className="input" type="range" min="0" max="100" step="1" value={simpleForm.credit_utilization} onChange={e=>setSimpleForm({...simpleForm, credit_utilization:Number(e.target.value)})} />
                <div className="small">{simpleForm.credit_utilization}% • Lower is healthier (aim &lt; 30%).</div>
              </div>
              <div className="stack" style={{padding:'8px',borderRadius:'6px',background:'rgba(165,180,252,0.05)'}}>
                <div className="label">Average Account Age (years)</div>
                <input className="input" type="range" min="0" max="30" step="1" value={simpleForm.credit_age_years} onChange={e=>setSimpleForm({...simpleForm, credit_age_years:Number(e.target.value)})} />
                <div className="small">{simpleForm.credit_age_years} yrs • Older average age helps.</div>
              </div>
              <div className="stack" style={{padding:'8px',borderRadius:'6px'}}>
                <div className="label">Credit Types (count)</div>
                <input className="input" type="range" min="1" max="10" step="1" value={simpleForm.credit_types_count} onChange={e=>setSimpleForm({...simpleForm, credit_types_count:Number(e.target.value)})} />
                <div className="small">{simpleForm.credit_types_count} • Diversity can help marginally.</div>
              </div>
              <div className="stack" style={{padding:'8px',borderRadius:'6px',background:'rgba(165,180,252,0.05)'}}>
                <div className="label">Recent Credit Inquiries (12m)</div>
                <input className="input" type="range" min="0" max="10" step="1" value={simpleForm.recent_inquiries_count} onChange={e=>setSimpleForm({...simpleForm, recent_inquiries_count:Number(e.target.value)})} />
                <div className="small">{simpleForm.recent_inquiries_count} • Fewer is better.</div>
              </div>
            </div>
          </div>
          <div className="col-6">
            <div className="stack" style={{gap:'10px'}}>
              <div className="kpi" style={{fontWeight:700,fontSize:'28px'}}>Score: {simpleScore ?? '—'} / 850</div>
              <div>
                <button className="btn btn-primary" onClick={runSimpleScore} disabled={simpleLoading} aria-label="Calculate simple credit score">
                  {simpleLoading ? 'Calculating…' : 'Calculate'}
                </button>
              </div>
              {simpleErr && <div className="small" style={{color:'#ff8b8b'}}>{simpleErr}</div>}
              {simpleUpdatedAt && <div className="small" style={{opacity:0.8}}>Updated: {simpleUpdatedAt.toLocaleTimeString()}</div>}
              {typeof simpleScore === 'number' && (
                <>
                  <div style={{width:'100%',height:'18px',background:'#1E1B3A',borderRadius:'10px',overflow:'hidden',border:'1px solid #A5B4FC'}}>
                    <div style={{
                      width: `${Math.max(0, Math.min(100, ((simpleScore - 300) / (850 - 300)) * 100))}%`,
                      height: '100%',
                      background: 'linear-gradient(to right, #61D29A, #A78BFA)',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                  <div className="small" style={{opacity:0.9}}>
                    {(simpleScore<580 && 'Poor') || (simpleScore<670 && 'Fair') || (simpleScore<740 && 'Good') || (simpleScore<800 && 'Very Good') || 'Excellent'} credit health
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
