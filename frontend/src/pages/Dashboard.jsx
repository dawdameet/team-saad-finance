import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function Dashboard({ onToast }) {
  const [kpis, setKpis] = useState({})
  const [series, setSeries] = useState([])
  const [range, setRange] = useState(localStorage.getItem('chart_range') || '3M')
  const [creditScore, setCreditScore] = useState(null)

  useEffect(() => {
    (async () => {
      try {
        // Fetch KPIs and set state correctly
        const kpiRes = await api('/api/dashboard/kpis')
        setKpis(kpiRes)

        // Fetch portfolio series and set state correctly
        const data = await api('/api/dashboard/portfolio_series?days=365')
        setSeries(Array.isArray(data?.series) ? data.series : [])

        // Optionally: handle credit score from localStorage and event listeners for dynamic updates
        try {
          const creditScore = localStorage.getItem('simple_credit_score')
          if (creditScore) setCreditScore(Number(creditScore))
          window.addEventListener('simple-credit-updated', () => {
            const updated = localStorage.getItem('simple_credit_score')
            if (updated) setCreditScore(Number(updated))
          })
        } catch (_) {}
      } catch (e) {
        onToast?.(e.message)
      }
    })()
  }, [])


  return (
    <div className="grid">
      <div className="col-12">
        <div className="row" style={{ gap: '16px' }}>
          <div className="card">
            <div className="kpi" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '20px' }}>₹</span> Savings
            </div>
            {}
            <div className="kpi v text-[#61D29A]">₹ -</div>
          </div>
          <div className="card">
            <div className="kpi" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '20px' }}>★</span> Credit Score
            </div>
            <div className="kpi v text-[#C4B5FD]">-</div>
          </div>
          <div className="card">
            <div className="kpi" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '20px' }}>%</span> Returns (est.)
            </div>
            <div className="kpi v text-[#61D29A]">-</div>
          </div>
          <div className="card">
            <div className="kpi" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '20px' }}>₹</span> Tax Liability
            </div>
            <div className="kpi v text-[#ff8b8b]">₹ -</div>
          </div>
        </div>
      </div>

      <div className="col-12 card">
        <h3>Portfolio Trend</h3>
        <div style={{ height: 320 }}>
          {}
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={[]} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
              <CartesianGrid stroke="#A5B4FC" strokeOpacity={0.15} vertical={false} />
              <XAxis dataKey="date" stroke="#E2E8F0" tick={{ fill: '#E2E8F0', fontSize: 12 }} />
              <YAxis stroke="#E2E8F0" tick={{ fill: '#E2E8F0', fontSize: 12 }} />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#A5B4FC" fill="#7c73e6" fillOpacity={0.25} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
