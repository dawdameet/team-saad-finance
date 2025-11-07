import React, { useEffect, useMemo, useState } from 'react'
import { api, ensureAuth } from '../lib/api.js'

const INVESTMENT_TYPES = ['stocks','bonds','real_estate','crypto','mutual_fund','gold']
const MARKET_COND = ['bear','neutral','bull']

function LabeledSlider({ label, min, max, step, value, onChange, format=(v)=>String(v) }){
  return (
    <div className="card" style={{marginBottom:12}}>
      <div className="row" style={{justifyContent:'space-between', alignItems:'center'}}>
        <div style={{fontWeight:600}}>{label}</div>
        <div style={{opacity:0.8}}>{format(value)}</div>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e=>onChange(Number(e.target.value))}
        className="slider"/>
      <div className="small" style={{display:'flex', justifyContent:'space-between'}}>
        <span>{format(min)}</span>
        <span>{format(max)}</span>
      </div>
    </div>
  )
}

function DiscreteSlider({ label, options, index, onChange }){
  return (
    <div className="card" style={{marginBottom:12}}>
      <div className="row" style={{justifyContent:'space-between', alignItems:'center'}}>
        <div style={{fontWeight:600}}>{label}</div>
        <div style={{opacity:0.8}}>{options[index]}</div>
      </div>
      <input type="range" min={0} max={options.length-1} step={1} value={index}
        onChange={e=>onChange(Number(e.target.value))}
        className="slider"/>
      <div className="small" style={{display:'flex', justifyContent:'space-between'}}>
        {options.map((o,i)=>(<span key={o} style={{fontSize:12, opacity:i===index?1:0.6}}>{o}</span>))}
      </div>
    </div>
  )
}

export default function JonesRoi({ onToast }){
  const [loading, setLoading] = useState(false)
  const [pred, setPred] = useState(null)

  const [principal, setPrincipal] = useState(100000)
  const [investmentIdx, setInvestmentIdx] = useState(0)
  const [interest, setInterest] = useState(0.07)
  const [timePeriod, setTimePeriod] = useState(3)
  const [avgPastReturn, setAvgPastReturn] = useState(0.12)
  const [volatility, setVolatility] = useState(0.3)
  const [fees, setFees] = useState(0.01)
  const [riskScore, setRiskScore] = useState(5)
  const [marketIdx, setMarketIdx] = useState(1)
  const [inflation, setInflation] = useState(0.05)
  const [econIndex, setEconIndex] = useState(100)

  useEffect(()=>{ ensureAuth().catch(()=>{}) }, [])

  const body = useMemo(()=>({
    principal,
    investment_type: INVESTMENT_TYPES[investmentIdx],
    interest,
    time_period: timePeriod,
    avg_past_return: avgPastReturn,
    volatility,
    fees,
    risk_score: Math.round(riskScore),
    market_condition: MARKET_COND[marketIdx],
    inflation_rate: inflation,
    economic_index: econIndex,
  }), [principal, investmentIdx, interest, timePeriod, avgPastReturn, volatility, fees, riskScore, marketIdx, inflation, econIndex])

  async function fetchPrediction(){
    setLoading(true)
    try{
      const r = await api('/api/roi/predict', { method:'POST', body })
      setPred(r.predicted_roi_percent)
    }catch(e){ onToast?.(String(e.message || e)); }
    finally{ setLoading(false) }
  }

  useEffect(()=>{ fetchPrediction() }, [body.principal, body.investment_type, body.interest, body.time_period, body.avg_past_return, body.volatility, body.fees, body.risk_score, body.market_condition, body.inflation_rate, body.economic_index])

  return (
    <div>
      <div className="title" style={{marginBottom:12}}>Jones's roi</div>
      <div className="grid" style={{gridTemplateColumns:'1fr', gap:12}}>
        <DiscreteSlider label="Investment Type" options={INVESTMENT_TYPES} index={investmentIdx} onChange={setInvestmentIdx} />
        <DiscreteSlider label="Market Condition" options={MARKET_COND} index={marketIdx} onChange={setMarketIdx} />
        <LabeledSlider label="Principal" min={1000} max={1000000} step={1000} value={principal} onChange={setPrincipal} format={(v)=>`₹${v.toLocaleString()}`} />
        <LabeledSlider label="Interest" min={0} max={0.3} step={0.005} value={interest} onChange={setInterest} format={(v)=>`${(v*100).toFixed(1)}%`} />
        <LabeledSlider label="Time Period (years)" min={1} max={30} step={1} value={timePeriod} onChange={setTimePeriod} format={(v)=>`${v}y`} />
        <LabeledSlider label="Avg Past Return" min={0} max={0.5} step={0.005} value={avgPastReturn} onChange={setAvgPastReturn} format={(v)=>`${(v*100).toFixed(1)}%`} />
        <LabeledSlider label="Volatility" min={0} max={1} step={0.01} value={volatility} onChange={setVolatility} format={(v)=>v.toFixed(2)} />
        <LabeledSlider label="Fees" min={0} max={0.05} step={0.001} value={fees} onChange={setFees} format={(v)=>`${(v*100).toFixed(1)}%`} />
        <LabeledSlider label="Risk Score" min={1} max={10} step={1} value={riskScore} onChange={setRiskScore} format={(v)=>`${Math.round(v)}`} />
        <LabeledSlider label="Inflation" min={0} max={0.2} step={0.005} value={inflation} onChange={setInflation} format={(v)=>`${(v*100).toFixed(1)}%`} />
        <LabeledSlider label="Economic Index" min={50} max={200} step={1} value={econIndex} onChange={setEconIndex} format={(v)=>`${v}`} />
      </div>

      <div className="card" style={{marginTop:16}}>
        <div className="row" style={{justifyContent:'space-between', alignItems:'center'}}>
          <div style={{fontWeight:700}}>Predicted Expected ROI</div>
          <div style={{fontSize:28, fontWeight:800}}>{loading? '…' : pred==null? '-' : `${pred.toFixed(2)}%`}</div>
        </div>
      </div>
    </div>
  )
}
