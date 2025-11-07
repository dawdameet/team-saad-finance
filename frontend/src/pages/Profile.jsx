// frontend/src/pages/Profile.jsx
import React, { useEffect, useState } from 'react'
import { getMe, updateMe } from '../lib/api.js'

export default function Profile({ onToast }){
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')

  useEffect(()=>{
    (async ()=>{
      try{
        const me = await getMe()
        setEmail(me.email || '')
        setFullName(me.full_name || '')
      }catch(err){
        onToast?.(String(err.message || err))
      }finally{
        setLoading(false)
      }
    })()
  },[])

  function strength(pw){
    let s = 0; if(pw.length>=8) s++; if(/[A-Z]/.test(pw)) s++; if(/[a-z]/.test(pw)) s++; if(/\d/.test(pw)) s++; if(/[^\w]/.test(pw)) s++;
    return Math.min(s,5)
  }

  function validate(){
    setError('')
    if(!fullName.trim()) return 'Full name cannot be empty.'
    if(password){
      if(password.length < 8) return 'New password must be at least 8 characters.'
      if(confirmPassword !== password) return 'Passwords do not match.'
    }
    return ''
  }

  async function handleSave(e){
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    const v = validate()
    if(v){ setError(v); setSaving(false); return }
    try{
      const body = { full_name: fullName }
      if(password) body.password = password
      const updated = await updateMe(body)
      setFullName(updated.full_name || '')
      setPassword('')
      setConfirmPassword('')
      setSaved(true)
      onToast?.('Profile updated!')
      setTimeout(()=>setSaved(false), 3000)
    }catch(err){
      onToast?.(String(err.message || err))
    }finally{
      setSaving(false)
    }
  }

  if(loading){
    return (
      <div className="card">
        <h2>Your Profile</h2>
        <div className="skeleton" style={{height:12, width:180, marginTop:8}}></div>
        <div className="skeleton" style={{height:12, width:240, marginTop:8}}></div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2>Your Profile</h2>
      <div className="flex items-center gap-3 mt-2" aria-label="profile header">
        <div style={{width:48,height:48,borderRadius:999,background:'#4C4686',display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontWeight:700}}>
          {(() => {
            const src = (fullName||'').trim() || (email||'').trim()
            const parts = src.split(/\s+/).filter(Boolean)
            const initials = parts.length>=2 ? (parts[0][0] + parts[1][0]) : src.slice(0,2)
            return initials.toUpperCase()
          })()}
        </div>
        <div className="text-sm" style={{color:'#E2E8F0'}}>
          <div style={{fontWeight:600}}>{fullName || '—'}</div>
          <div style={{opacity:0.8}}>{email}</div>
        </div>
      </div>
      <form onSubmit={handleSave} className="space-y-4 mt-3 max-w-xl">
        <div>
          <label className="block text-xs text-[#9CA3AF] mb-1" style={{fontStyle:'italic'}}>Email (read-only)</label>
          <div style={{position:'relative'}}>
            <input className="input" type="email" value={email} readOnly />
            <button 
              type="button"
              onClick={()=>{navigator.clipboard.writeText(email);onToast?.('Email copied!')}}
              style={{position:'absolute',right:'10px',top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',fontSize:'16px'}}
              aria-label="Copy email to clipboard"
            >
              📋
            </button>
          </div>
        </div>
        <div>
          <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Full name</label>
          <input className="input" type="text" value={fullName} onChange={e=>setFullName(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>New Password</label>
          <div style={{position:'relative'}}>
            <input className="input" type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} placeholder="Leave blank to keep current" />
            <button 
              type="button"
              onClick={()=>setShowPassword(!showPassword)}
              style={{position:'absolute',right:'10px',top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',fontSize:'16px'}}
              aria-label="Toggle password visibility"
            >
              {showPassword?'👁️':'👁️‍🗨️'}
            </button>
          </div>
          {password && (
            <div className="mt-1" aria-label="password strength">
              <div style={{height:6, borderRadius:6, background:'rgba(255,255,255,0.1)'}}>
                <div style={{height:'100%', width:`${(strength(password)/5)*100}%`, background: strength(password)>=4?'#10B981': strength(password)>=3?'#F59E0B':'#EF4444', borderRadius:6}}></div>
              </div>
              <div className="text-[11px] text-[#E2E8F0] mt-1" style={{opacity:0.85}}>{strength(password)>=4?'Strong':strength(password)>=3?'Medium':'Weak'}</div>
            </div>
          )}
        </div>
        {password && (
          <div>
            <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Confirm New Password</label>
            <input className="input" type={showPassword?'text':'password'} value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)} placeholder="Re-enter new password" />
          </div>
        )}
        {error && (
          <div className="text-xs" style={{color:'#ff8b8b'}}>{error}</div>
        )}
        <button 
          type="submit" 
          className="btn" 
          style={{background:saved?'#10B981':'linear-gradient(135deg,#A78BFA,#8B5CF6)',borderColor:saved?'#10B981':'#8B5CF6',color:'#FFFFFF'}}
          disabled={saving}
          aria-label="Save profile changes"
        >
          {saving ? 'Saving…' : saved ? '✓ Saved!' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
