// frontend/src/pages/Login.jsx
import React, { useState } from 'react'
import { register as apiRegister, login as apiLogin } from '../lib/api.js'

export default function Login({ onLoggedIn, onToast }){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [loading, setLoading] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')

  function validate(){
    setError('')
    if(!email.trim()) return 'Email is required.'
    const emailOk = /.+@.+\..+/.test(email)
    if(!emailOk) return 'Please enter a valid email address.'
    if(!password) return 'Password is required.'
    if(password.length < 8) return 'Password must be at least 8 characters.'
    if(mode === 'register'){
      if(!fullName.trim()) return 'Please enter your full name.'
      if(!confirmPassword) return 'Please confirm your password.'
      if(confirmPassword !== password) return 'Passwords do not match.'
    }
    return ''
  }

  function strength(pw){
    let s = 0; if(pw.length>=8) s++; if(/[A-Z]/.test(pw)) s++; if(/[a-z]/.test(pw)) s++; if(/\d/.test(pw)) s++; if(/[^\w]/.test(pw)) s++;
    return Math.min(s,5)
  }

  async function handleSubmit(e){
    e.preventDefault()
    setLoading(true)
    const v = validate()
    if(v){ setError(v); setLoading(false); return }
    try{
      if(mode === 'register'){
        await apiRegister(email, password, fullName)
      }else{
        await apiLogin(email, password)
      }
      onLoggedIn?.()
    }catch(err){
      const msg = String(err.message || err)
      setError(msg)
      onToast?.(msg)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#1E1B3A] flex items-center justify-center p-4" style={{position:'relative',overflow:'hidden'}}>
      {/* soft gradient accents */}
      <div style={{position:'absolute',inset:0,pointerEvents:'none'}} aria-hidden>
        <div style={{position:'absolute',width:420,height:420,background:'radial-gradient(closest-side, rgba(167,139,250,0.25), transparent 70%)',top:-80,left:-80,filter:'blur(10px)'}} />
        <div style={{position:'absolute',width:520,height:520,background:'radial-gradient(closest-side, rgba(99,102,241,0.18), transparent 70%)',bottom:-120,right:-120,filter:'blur(12px)'}} />
      </div>
      <div className="w-full max-w-sm" style={{position:'relative', maxWidth:360}}>
        <div className="text-center mb-6">
          <div style={{display:'inline-flex',alignItems:'center',justifyContent:'center',width:56,height:56,borderRadius:14,background:'linear-gradient(135deg,#8B5CF6,#6366F1)',boxShadow:'0 10px 30px rgba(99,102,241,0.35)'}}>⚡</div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-3">FinEdge Pro</h1>
          <p className="text-sm text-[#E2E8F0] mt-1" style={{opacity:0.9}}>{mode==='login' ? 'Sign in to continue' : 'Create your account'}</p>
        </div>
        <div className="rounded-2xl border border-[#A5B4FC] bg-[#2a2750] shadow-card p-5" style={{backdropFilter:'blur(6px)', boxShadow:'0 10px 40px rgba(20,18,43,0.6)'}}>
          {/* segmented mode switch */}
          <div className="flex mb-4" role="tablist" aria-label="auth mode">
            <button type="button" onClick={()=>{setMode('login');setError('')}} className={"btn btn-ghost" + (mode==='login'?' active':'')} style={{flex:1,borderRadius:10,marginRight:6}}>Sign In</button>
            <button type="button" onClick={()=>{setMode('register');setError('')}} className={"btn btn-ghost" + (mode==='register'?' active':'')} style={{flex:1,borderRadius:10,marginLeft:6}}>Create Account</button>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode==='register' && (
              <div>
                <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Full name</label>
                <input className="input focus:outline-none w-full" type="text" value={fullName} onChange={e=>setFullName(e.target.value)} placeholder="Your Name" />
              </div>
            )}
            <div>
              <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Email</label>
              <input className="input focus:outline-none w-full" type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div>
              <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Password</label>
              <div style={{position:'relative'}}>
                <input className="input focus:outline-none w-full" type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 8 characters" />
                <button type="button" onClick={()=>setShowPassword(!showPassword)} style={{position:'absolute',right:10,top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',fontSize:'16px'}} aria-label="Toggle password visibility">{showPassword?'👁️':'👁️‍🗨️'}</button>
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
            {mode==='register' && (
              <div>
                <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Confirm Password</label>
                <input className="input focus:outline-none w-full" type={showPassword?'text':'password'} value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)} placeholder="Re-enter password" />
              </div>
            )}
            {error && (
              <div className="text-xs" style={{color:'#ff8b8b'}}>{error}</div>
            )}
            <button type="submit" disabled={loading} className="btn btn-primary w-full">
              {loading ? (mode==='login' ? 'Signing in…' : 'Creating account…') : (mode==='login' ? 'Sign In' : 'Create Account')}
            </button>
          </form>
          <div className="text-xs text-[#E2E8F0] mt-3 text-center" style={{opacity:0.9}}>
            By continuing you agree to our <span className="text-[#C4B5FD]">Terms</span> and <span className="text-[#C4B5FD]">Privacy</span>.
          </div>
        </div>
      </div>
    </div>
  )
}
