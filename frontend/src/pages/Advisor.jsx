// frontend/src/pages/Advisor.jsx
import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'

export default function Advisor({ onToast }){
  const [symbols, setSymbols] = useState([])
  const [symbol, setSymbol] = useState('')
  const [buyPrice, setBuyPrice] = useState('0')
  const [quantity, setQuantity] = useState('1')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  function formatINR(n){
    const x = Number(n)
    if(!Number.isFinite(x)) return 'N/A'
    try{ return new Intl.NumberFormat('en-IN', { style:'currency', currency:'INR' }).format(x) }catch(_){ return `₹ ${x.toLocaleString('en-IN')}` }
  }

  useEffect(()=>{
    (async ()=>{
      try{
        const list = await api('/api/advisor/symbols')
        setSymbols(list)
        if(list.length) setSymbol(list[0])
      }catch(e){ onToast?.(e.message); setError(e.message) }
    })()
  },[])

  async function onSubmit(e){
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try{
      const data = await api('/api/advisor/recommend', {
        method: 'POST',
        body: {
          symbol: symbol,
          buy_price: parseFloat(buyPrice || '0'),
          quantity: parseInt(quantity || '1', 10)
        }
      })}}
      setResult(data)
      onToast?.('Advisor recommendation ready')
    }catch(err){
      const msg = err?.message || 'Failed to get recommendation'
      setError(msg)
      onToast?.(msg)
    }finally{
      setLoading(false)
    }
  }}}

  return ({{
    <div className="card">
      <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:6}}>
        <div style={{width:36,height:36,borderRadius:10,display:'flex',alignItems:'center',justifyContent:'center',background:'linear-gradient(135deg,#8B5CF6,#6366F1)'}}>📊</div>
        <div className="card-title" style={{margin:0}}>Stock Advisor</div>
      </div>
      <div className="grid" style={{gap:12}}>
        <div className="col-6">
          <form onSubmit={onSubmit} className="stack" style={{gap:10}}>
            <label className="stack">
              <div className="label">Symbol</div>
              <select value={symbol} onChange={e=>setSymbol(e.target.value)} className="input">
                {symbols.map(s => (<option key={s} value={s}>{s}</option>))}
              </select>
              <div className="small" style={{opacity:0.85}}>Select from available symbols.</div>
            </label>
            <div className="grid" style={{gap:10}}>
              <label className="col-6 stack">
                <div className="label">Buy Price (₹)</div>
                <input className="input" type="number" step="0.01" value={buyPrice} onChange={e=>setBuyPrice(e.target.value)} />
                <div className="small" style={{opacity:0.85}}>Your intended purchase price.</div>
              </label>
              <label className="col-6 stack">
                <div className="label">Quantity</div>
                <input className="input" type="number" min="1" value={quantity} onChange={e=>setQuantity(e.target.value)} />
                <div className="small" style={{opacity:0.85}}>Number of shares.</div>
              </label>
            </div>
            <div>
              <button className="btn btn-primary" type="submit" disabled={loading || !symbol}>{loading ? 'Analyzing…' : 'Get Recommendation'}</button>
            </div>
          </form>
          {error && (
            <div className="alert error" style={{marginTop:12}}>{error}</div>
          )}
        </div>
        <div className="col-6">
          <div className="card" style={{height:'100%'}}>
            <div className="card-title">Result</div>
            {result ? (
              <div className="grid grid-2" style={{gap:10}}>
                <div>
                  <div className="small text-muted">Symbol</div>
                  <div>{result.symbol}</div>
                </div>
                <div>
                  <div className="small text-muted">Latest Close</div>
                  <div>{result.latest_close != null ? formatINR(result.latest_close) : 'N/A'}</div>
                </div>
                <div>
                  <div className="small text-muted">Probability Up</div>
                  <div>{result.prob_up != null ? `${(Number(result.prob_up)*100).toFixed(1)}%` : 'N/A'}</div>
                </div>
                <div>
                  <div className="small text-muted">Unrealized P/L</div>
                  <div style={{color: Number(result.profit_loss)>=0 ? '#61D29A' : '#ff8b8b'}}>
                    {result.profit_loss != null ? formatINR(result.profit_loss) : 'N/A'}
                  </div>
                </div>
                <div style={{gridColumn:'1 / -1'}}>
                  <div className="small text-muted">Decision</div>
                  <div>
                    <span className="badge" style={{borderRadius:999, padding:'4px 10px', background:'rgba(167,139,250,0.12)', border:'1px solid #A5B4FC'}}>
                      {result.decision || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="small" style={{opacity:0.9}}>Fill the form and click Get Recommendation to see insights here.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
