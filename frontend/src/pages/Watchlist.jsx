import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'

export default function Watchlist({ onToast }){
  const [items, setItems] = useState([])
  const [symbol, setSymbol] = useState('')
  const [loading, setLoading] = useState(false)
  const [adding, setAdding] = useState(false)

  async function load(){
    setLoading(true)
    try{
      const res = await api('/api/watchlist/')
      setItems(res.items || [])
    }catch(e){ onToast?.(e.message || 'Failed to load watchlist') }
    finally{ setLoading(false) }
  }

  useEffect(()=>{ load() },[])

  async function addSymbol(){
    const s = (symbol||'').trim()
    if(!s) return
    try{
      setAdding(true)
      await api('/api/watchlist/', { method:'POST', body:{ symbol: s } })
      setSymbol('')
      await load()
      onToast?.(`Added ${s}`)
    }catch(e){ onToast?.(e.message || 'Failed to add') }
    finally{ setAdding(false) }
  }

  async function removeSymbol(s){
    try{
      await api(`/api/watchlist/${encodeURIComponent(s)}`, { method:'DELETE' })
      await load()
      onToast?.(`Removed ${s}`)
    }catch(e){ onToast?.(e.message || 'Failed to remove') }
  }

  return (
    <div>
      <div className="card" style={{marginBottom:16}}>
        <div className="card-title" style={{display:'flex', alignItems:'center', gap:8}}>
          <span role="img" aria-label="eyes">👀</span>
          <span>Watchlist</span>
        </div>
        <div className="row" style={{gap:8}}>
          <input
            className="input"
            placeholder="Enter symbol (e.g., AAPL)"
            value={symbol}
            onChange={e=>setSymbol(e.target.value)}
            onKeyDown={e=>{ if(e.key==='Enter') addSymbol() }}
            style={{maxWidth:240}}
          />
          <button className="btn btn-primary" onClick={addSymbol} disabled={adding}>{adding?'Adding…':'Add'}</button>
          <button className="btn btn-secondary" onClick={load} disabled={loading}>{loading?'Refreshing…':'Refresh'}</button>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Symbols</div>
        {loading && (
          <div className="stack" style={{gap:12}}>
            <div className="skeleton" style={{height:44}}></div>
            <div className="skeleton" style={{height:44}}></div>
            <div className="skeleton" style={{height:44}}></div>
          </div>
        )}
        {!loading && items.length === 0 && (
          <div className="small">No symbols yet. Add one above.</div>
        )}
        {!loading && items.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Price</th>
                <th>% Change</th>
                <th>SMA20</th>
                <th>RSI14</th>
                <th>Pred Next</th>
                <th>Model</th>
                <th style={{width:120}}></th>
              </tr>
            
              {items.map(it=> {
                const pct = Number(it.percent_change ?? 0)
                const pctColor = pct > 0 ? 'var(--ok)' : (pct < 0 ? '#ef4444' : 'var(--muted)')
                const fmt = (v, d=2) => (v==null || Number.isNaN(Number(v))) ? 'N/A' : Number(v).toFixed(d)
                return (
                  <tr key={it.symbol}>
                    <td><span className="badge">{it.symbol}</span></td>
                    <td>₹ {fmt(it.price, 2)}</td>
                    <td style={{color:pctColor, fontWeight:600}}>{fmt(pct, 2)}%</td>
                    <td>{fmt(it.SMA20, 2)}</td>
                    <td>{fmt(it.RSI14, 2)}</td>
                    <td style={{fontFamily:'ui-monospace, SFMono-Regular, Menlo, monospace'}}>{fmt(it.pred_return, 4)}</td>
                    <td>{it.pred_model?.toUpperCase?.() || 'NAIVE'}</td>
                    <td>
                      <button className="btn btn-secondary" onClick={()=>removeSymbol(it.symbol)}>Remove</button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
